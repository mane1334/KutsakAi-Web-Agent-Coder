"""
Sistema de Configuração Centralizada para KutsakAI Web Agent Builder
"""

import os
import yaml
import json
from typing import Any, Dict, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """Gerenciador de configuração centralizada com suporte a múltiplos formatos."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Implementa padrão Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, config_file: str = "config.yaml"):
        """Inicializa o gerenciador de configuração."""
        if self._initialized:
            return
            
        self.config_file = Path(config_file)
        self.config = {}
        self.watchers = {}  # Para callbacks de mudanças
        self._load_config()
        self._initialized = True
    
    def _load_config(self) -> None:
        """Carrega a configuração do arquivo."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    if self.config_file.suffix.lower() == '.yaml' or self.config_file.suffix.lower() == '.yml':
                        self.config = yaml.safe_load(f) or {}
                    elif self.config_file.suffix.lower() == '.json':
                        self.config = json.load(f)
                    else:
                        raise ValueError(f"Formato de arquivo não suportado: {self.config_file.suffix}")
                        
                logger.info(f"Configuração carregada de {self.config_file}")
            else:
                logger.warning(f"Arquivo de configuração não encontrado: {self.config_file}")
                self.config = self._get_default_config()
                self.save_config()
                
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna a configuração padrão."""
        return {
            "app": {
                "name": "KutsakAI Web Agent Builder",
                "version": "2.1.0",
                "debug": False,
                "auto_save": True,
                "backup_interval": 300
            },
            "ollama": {
                "base_url": "http://localhost:11434",
                "default_model": "codellama",
                "timeout": 300,
                "max_retries": 3,
                "circuit_breaker": {
                    "failure_threshold": 5,
                    "timeout": 60
                }
            },
            "ui": {
                "theme": "dark",
                "language": "pt-BR",
                "window": {
                    "width": 1400,
                    "height": 900,
                    "min_width": 1000,
                    "min_height": 700
                },
                "fonts": {
                    "default_family": "Inter, Segoe UI Variable, SF Pro Display, Roboto, sans-serif",
                    "default_size": 13,
                    "code_family": "JetBrains Mono, Fira Code, Consolas, monospace",
                    "code_size": 12
                }
            },
            "performance": {
                "cache_enabled": True,
                "cache_size": 100,
                "cache_ttl": 3600,
                "max_workers": 4,
                "chunk_size": 1024
            },
            "logging": {
                "level": "INFO",
                "file": "app.log",
                "max_size": 10485760,
                "backup_count": 5,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "plugins": {
                "enabled": True,
                "directory": "plugins",
                "auto_load": True
            },
            "projects": {
                "default_directory": "projects",
                "auto_backup": True,
                "backup_interval": 600,
                "max_recent_projects": 10
            },
            "security": {
                "enable_code_execution_sandbox": True,
                "allowed_file_extensions": [".html", ".css", ".js", ".py", ".md", ".txt", ".json", ".yaml"],
                "max_file_size": 5242880
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtém um valor da configuração usando notação de ponto.
        
        Args:
            key_path: Caminho da chave (ex: 'ui.theme', 'ollama.timeout')
            default: Valor padrão se a chave não existir
            
        Returns:
            Valor da configuração ou valor padrão
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any, save: bool = True) -> None:
        """
        Define um valor na configuração usando notação de ponto.
        
        Args:
            key_path: Caminho da chave (ex: 'ui.theme')
            value: Valor a ser definido
            save: Se deve salvar automaticamente
        """
        keys = key_path.split('.')
        config_ref = self.config
        
        # Navega até o penúltimo nível
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        # Define o valor
        old_value = config_ref.get(keys[-1])
        config_ref[keys[-1]] = value
        
        # Notifica watchers
        self._notify_watchers(key_path, old_value, value)
        
        if save:
            self.save_config()
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> None:
        """
        Atualiza múltiplos valores na configuração.
        
        Args:
            updates: Dicionário com as atualizações
            save: Se deve salvar automaticamente
        """
        for key_path, value in updates.items():
            self.set(key_path, value, save=False)
        
        if save:
            self.save_config()
    
    def save_config(self) -> None:
        """Salva a configuração no arquivo."""
        try:
            # Cria o diretório se não existir
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.suffix.lower() in ['.yaml', '.yml']:
                    yaml.dump(self.config, f, default_flow_style=False, 
                             allow_unicode=True, sort_keys=False)
                elif self.config_file.suffix.lower() == '.json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                    
            logger.info(f"Configuração salva em {self.config_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar configuração: {e}")
    
    def reload(self) -> None:
        """Recarrega a configuração do arquivo."""
        self._load_config()
        logger.info("Configuração recarregada")
    
    def watch(self, key_path: str, callback) -> None:
        """
        Registra um callback para ser chamado quando uma configuração mudar.
        
        Args:
            key_path: Caminho da chave para observar
            callback: Função a ser chamada (callback(key_path, old_value, new_value))
        """
        if key_path not in self.watchers:
            self.watchers[key_path] = []
        self.watchers[key_path].append(callback)
    
    def unwatch(self, key_path: str, callback) -> None:
        """Remove um watcher."""
        if key_path in self.watchers:
            try:
                self.watchers[key_path].remove(callback)
                if not self.watchers[key_path]:
                    del self.watchers[key_path]
            except ValueError:
                pass
    
    def _notify_watchers(self, key_path: str, old_value: Any, new_value: Any) -> None:
        """Notifica os watchers sobre mudanças."""
        if key_path in self.watchers:
            for callback in self.watchers[key_path]:
                try:
                    callback(key_path, old_value, new_value)
                except Exception as e:
                    logger.error(f"Erro no callback do watcher: {e}")
    
    def export_config(self, file_path: str, format_type: str = 'yaml') -> None:
        """
        Exporta a configuração para um arquivo.
        
        Args:
            file_path: Caminho do arquivo
            format_type: Formato ('yaml' ou 'json')
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type.lower() == 'yaml':
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                elif format_type.lower() == 'json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                else:
                    raise ValueError(f"Formato não suportado: {format_type}")
                    
            logger.info(f"Configuração exportada para {file_path}")
            
        except Exception as e:
            logger.error(f"Erro ao exportar configuração: {e}")
            raise
    
    def validate_config(self) -> list:
        """
        Valida a configuração atual.
        
        Returns:
            Lista de erros encontrados
        """
        errors = []
        
        # Validações básicas
        required_keys = ['app', 'ollama', 'ui', 'performance']
        for key in required_keys:
            if key not in self.config:
                errors.append(f"Seção obrigatória ausente: {key}")
        
        # Validação específica do Ollama
        ollama_config = self.config.get('ollama', {})
        if 'base_url' not in ollama_config:
            errors.append("ollama.base_url é obrigatório")
        
        # Validação de tipos
        if not isinstance(self.get('performance.cache_size'), int):
            errors.append("performance.cache_size deve ser um inteiro")
        
        if not isinstance(self.get('performance.cache_ttl'), int):
            errors.append("performance.cache_ttl deve ser um inteiro")
        
        return errors
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Retorna uma seção completa da configuração."""
        return self.config.get(section, {})
    
    def has_key(self, key_path: str) -> bool:
        """Verifica se uma chave existe na configuração."""
        return self.get(key_path, None) is not None

# Instância global do gerenciador
config = ConfigManager()

# Função helper para facilitar o uso
def get_config(key_path: str, default: Any = None) -> Any:
    """Função helper para obter configurações."""
    return config.get(key_path, default)

def set_config(key_path: str, value: Any, save: bool = True) -> None:
    """Função helper para definir configurações."""
    config.set(key_path, value, save)

def reload_config() -> None:
    """Função helper para recarregar configurações."""
    config.reload()
