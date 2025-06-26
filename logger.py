"""
Sistema de Logging Estruturado e Monitoramento para KutsakAI Web Agent Builder
"""

import logging
import logging.handlers
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import traceback
from functools import wraps
import threading
from collections import defaultdict, deque

from config_manager import get_config

class JSONFormatter(logging.Formatter):
    """Formatter customizado para logs em formato JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log em JSON estruturado."""
        log_obj = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Adiciona informações extras se disponíveis
        if hasattr(record, 'extra'):
            log_obj.update(record.extra)
        
        # Adiciona traceback para erros
        if record.exc_info:
            log_obj['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        return json.dumps(log_obj, ensure_ascii=False)

class PerformanceMonitor:
    """Monitor de performance para funções."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_execution_time(self, function_name: str, execution_time: float, **kwargs):
        """Registra tempo de execução de uma função."""
        with self.lock:
            metric = {
                'timestamp': datetime.now().isoformat(),
                'execution_time': execution_time,
                **kwargs
            }
            self.metrics[function_name].append(metric)
            
            # Manter apenas os últimos 1000 registros por função
            if len(self.metrics[function_name]) > 1000:
                self.metrics[function_name] = self.metrics[function_name][-1000:]
    
    def get_statistics(self, function_name: str) -> Dict[str, Any]:
        """Obtém estatísticas de uma função."""
        with self.lock:
            if function_name not in self.metrics:
                return {}
            
            times = [m['execution_time'] for m in self.metrics[function_name]]
            if not times:
                return {}
            
            return {
                'count': len(times),
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times),
                'last_execution': self.metrics[function_name][-1]['timestamp']
            }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Obtém estatísticas de todas as funções."""
        with self.lock:
            return {func: self.get_statistics(func) for func in self.metrics.keys()}

class StructuredLogger:
    """Logger estruturado principal."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa padrão Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa o logger estruturado."""
        if self._initialized:
            return
            
        self.logger = logging.getLogger("kutsakai")
        self.performance_monitor = PerformanceMonitor()
        self.events_buffer = deque(maxlen=1000)  # Buffer para eventos recentes
        self._setup_logger()
        self._initialized = True
    
    def _setup_logger(self):
        """Configura o sistema de logging."""
        # Remove handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Configurações do arquivo de configuração
        log_level = get_config('logging.level', 'INFO')
        log_file = get_config('logging.file', 'app.log')
        max_size = get_config('logging.max_size', 10485760)  # 10MB
        backup_count = get_config('logging.backup_count', 5)
        
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Handler para arquivo com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_size, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(file_handler)
        
        # Handler para console (apenas em modo debug)
        if get_config('app.debug', False):
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def log_event(self, event_type: str, message: str = "", level: str = "info", **kwargs):
        """
        Registra um evento estruturado.
        
        Args:
            event_type: Tipo do evento (ex: 'code_generation', 'user_action')
            message: Mensagem descritiva
            level: Nível do log (debug, info, warning, error, critical)
            **kwargs: Dados adicionais do evento
        """
        event_data = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': kwargs
        }
        
        # Adiciona ao buffer de eventos
        self.events_buffer.append(event_data)
        
        # Cria o record de log
        extra = {'extra': event_data}
        getattr(self.logger, level.lower())(message, extra=extra)
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Registra ação do usuário."""
        self.log_event(
            'user_action',
            f"User action: {action}",
            level='info',
            action=action,
            details=details or {}
        )
    
    def log_ai_request(self, model: str, prompt_length: int, response_length: int = None, 
                      execution_time: float = None, error: str = None):
        """Registra requisição para IA."""
        event_data = {
            'model': model,
            'prompt_length': prompt_length,
            'response_length': response_length,
            'execution_time': execution_time
        }
        
        if error:
            event_data['error'] = error
            level = 'error'
            message = f"AI request failed: {error}"
        else:
            level = 'info'
            message = f"AI request completed: {model}"
        
        self.log_event('ai_request', message, level=level, **event_data)
    
    def log_performance(self, operation: str, execution_time: float, **kwargs):
        """Registra métrica de performance."""
        self.performance_monitor.record_execution_time(operation, execution_time, **kwargs)
        self.log_event(
            'performance',
            f"Operation {operation} took {execution_time:.3f}s",
            level='debug',
            operation=operation,
            execution_time=execution_time,
            **kwargs
        )
    
    def log_error(self, error: Exception, context: str = "", **kwargs):
        """Registra erro com contexto."""
        self.log_event(
            'error',
            f"Error in {context}: {str(error)}",
            level='error',
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            **kwargs
        )
        
        # Log completo com traceback
        self.logger.error(f"Error in {context}", exc_info=True)
    
    def get_recent_events(self, event_type: str = None, limit: int = 100) -> list:
        """Obtém eventos recentes."""
        events = list(self.events_buffer)
        
        if event_type:
            events = [e for e in events if e['event_type'] == event_type]
        
        return events[-limit:]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de performance."""
        return self.performance_monitor.get_all_statistics()
    
    def debug(self, message: str, **kwargs):
        """Log de debug."""
        self.log_event('debug', message, level='debug', **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log de informação."""
        self.log_event('info', message, level='info', **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log de aviso."""
        self.log_event('warning', message, level='warning', **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log de erro."""
        self.log_event('error', message, level='error', **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log crítico."""
        self.log_event('critical', message, level='critical', **kwargs)

# Instância global do logger
logger = StructuredLogger()

# Decorador para monitoramento de performance
def monitor_performance(operation_name: str = None):
    """
    Decorador para monitorar performance de funções.
    
    Args:
        operation_name: Nome da operação (usa nome da função se não especificado)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                logger.log_performance(
                    op_name,
                    execution_time,
                    success=True,
                    args_count=len(args),
                    kwargs_count=len(kwargs)
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                logger.log_performance(
                    op_name,
                    execution_time,
                    success=False,
                    error=str(e)
                )
                
                logger.log_error(e, f"Function {op_name}")
                raise
        
        return wrapper
    return decorator

# Decorador para logging de entrada e saída de funções
def log_calls(level: str = 'debug'):
    """
    Decorador para logar chamadas de função.
    
    Args:
        level: Nível do log
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            
            # Log entrada
            logger.log_event(
                'function_call',
                f"Calling {func_name}",
                level=level,
                function=func_name,
                event='enter',
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Log saída
                logger.log_event(
                    'function_call',
                    f"Completed {func_name}",
                    level=level,
                    function=func_name,
                    event='exit',
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Log erro
                logger.log_event(
                    'function_call',
                    f"Failed {func_name}: {str(e)}",
                    level='error',
                    function=func_name,
                    event='error',
                    error=str(e)
                )
                raise
        
        return wrapper
    return decorator

# Context manager para operações complexas
class LogContext:
    """Context manager para operações complexas com logging."""
    
    def __init__(self, operation: str, **kwargs):
        self.operation = operation
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.log_event(
            'operation_start',
            f"Starting {self.operation}",
            level='info',
            operation=self.operation,
            **self.kwargs
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            logger.log_event(
                'operation_complete',
                f"Completed {self.operation} in {execution_time:.3f}s",
                level='info',
                operation=self.operation,
                execution_time=execution_time,
                success=True,
                **self.kwargs
            )
        else:
            logger.log_event(
                'operation_failed',
                f"Failed {self.operation} after {execution_time:.3f}s: {str(exc_val)}",
                level='error',
                operation=self.operation,
                execution_time=execution_time,
                success=False,
                error=str(exc_val),
                **self.kwargs
            )
    
    def log(self, message: str, level: str = 'info', **kwargs):
        """Log dentro do contexto da operação."""
        logger.log_event(
            'operation_log',
            message,
            level=level,
            operation=self.operation,
            **kwargs
        )

# Função helper para obter o logger
def get_logger() -> StructuredLogger:
    """Retorna a instância do logger estruturado."""
    return logger
