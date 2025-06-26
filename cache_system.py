"""
Sistema de Cache Inteligente para KutsakAI Web Agent Builder
"""

import hashlib
import json
import time
import threading
from typing import Any, Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from abc import ABC, abstractmethod
import pickle
import zlib
from datetime import datetime, timedelta

from config_manager import get_config
from logger import get_logger, monitor_performance

logger = get_logger()

@dataclass
class CacheEntry:
    """Entrada do cache com metadados."""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    size_bytes: int = 0
    ttl: Optional[float] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

class CacheBackend(ABC):
    """Interface abstrata para backends de cache."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[CacheEntry]:
        pass
    
    @abstractmethod
    def set(self, key: str, entry: CacheEntry) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        pass
    
    @abstractmethod
    def keys(self) -> List[str]:
        pass
    
    @abstractmethod
    def size(self) -> int:
        pass

class MemoryBackend(CacheBackend):
    """Backend de cache em memória."""
    
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # Para LRU
        self.lock = threading.RLock()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                entry.access_count += 1
                
                # Atualiza ordem de acesso (LRU)
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                
                return entry
            return None
    
    def set(self, key: str, entry: CacheEntry) -> bool:
        with self.lock:
            # Remove entrada antiga se existir
            if key in self.cache:
                self.delete(key)
            
            # Verifica limite de tamanho
            while len(self.cache) >= self.max_size:
                # Remove entrada menos recentemente usada
                if self.access_order:
                    oldest_key = self.access_order.pop(0)
                    del self.cache[oldest_key]
                else:
                    break
            
            self.cache[key] = entry
            self.access_order.append(key)
            return True
    
    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
                return True
            return False
    
    def clear(self) -> bool:
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            return True
    
    def keys(self) -> List[str]:
        with self.lock:
            return list(self.cache.keys())
    
    def size(self) -> int:
        with self.lock:
            return len(self.cache)

class SQLiteBackend(CacheBackend):
    """Backend de cache persistente usando SQLite."""
    
    def __init__(self, db_path: str = "cache.db"):
        self.db_path = Path(db_path)
        self.lock = threading.RLock()
        self._init_db()
    
    def _init_db(self):
        """Inicializa o banco de dados."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS cache_entries (
                        key TEXT PRIMARY KEY,
                        value BLOB,
                        timestamp REAL,
                        access_count INTEGER DEFAULT 0,
                        size_bytes INTEGER DEFAULT 0,
                        ttl REAL,
                        tags TEXT,
                        metadata TEXT
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON cache_entries(timestamp)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_ttl ON cache_entries(ttl)
                """)
                conn.commit()
            finally:
                conn.close()
    
    def get(self, key: str) -> Optional[CacheEntry]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute(
                    "SELECT * FROM cache_entries WHERE key = ?", (key,)
                )
                row = cursor.fetchone()
                
                if row:
                    # Descompacta dados
                    _, value_blob, timestamp, access_count, size_bytes, ttl, tags_json, metadata_json = row
                    
                    try:
                        value = pickle.loads(zlib.decompress(value_blob))
                        tags = json.loads(tags_json) if tags_json else []
                        metadata = json.loads(metadata_json) if metadata_json else {}
                        
                        # Atualiza contador de acesso
                        conn.execute(
                            "UPDATE cache_entries SET access_count = access_count + 1 WHERE key = ?",
                            (key,)
                        )
                        conn.commit()
                        
                        return CacheEntry(
                            key=key,
                            value=value,
                            timestamp=timestamp,
                            access_count=access_count + 1,
                            size_bytes=size_bytes,
                            ttl=ttl,
                            tags=tags,
                            metadata=metadata
                        )
                    except Exception as e:
                        logger.error(f"Erro ao deserializar entrada do cache: {e}")
                        return None
                
                return None
                
            finally:
                conn.close()
    
    def set(self, key: str, entry: CacheEntry) -> bool:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                # Serializa dados
                value_blob = zlib.compress(pickle.dumps(entry.value))
                tags_json = json.dumps(entry.tags)
                metadata_json = json.dumps(entry.metadata)
                
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (key, value, timestamp, access_count, size_bytes, ttl, tags, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key, value_blob, entry.timestamp, entry.access_count,
                    len(value_blob), entry.ttl, tags_json, metadata_json
                ))
                conn.commit()
                return True
                
            except Exception as e:
                logger.error(f"Erro ao salvar entrada no cache: {e}")
                return False
            finally:
                conn.close()
    
    def delete(self, key: str) -> bool:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
                return cursor.rowcount > 0
            finally:
                conn.close()
    
    def clear(self) -> bool:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute("DELETE FROM cache_entries")
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Erro ao limpar cache: {e}")
                return False
            finally:
                conn.close()
    
    def keys(self) -> List[str]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("SELECT key FROM cache_entries")
                return [row[0] for row in cursor.fetchall()]
            finally:
                conn.close()
    
    def size(self) -> int:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.execute("SELECT COUNT(*) FROM cache_entries")
                return cursor.fetchone()[0]
            finally:
                conn.close()

class IntelligentCache:
    """Sistema de cache inteligente com múltiplas estratégias."""
    
    def __init__(self, backend: Optional[CacheBackend] = None):
        self.backend = backend or self._create_default_backend()
        self.hit_count = 0
        self.miss_count = 0
        self.lock = threading.RLock()
        
        # Configurações
        self.default_ttl = get_config('performance.cache_ttl', 3600)
        self.max_size = get_config('performance.cache_size', 100)
        
        # Inicia limpeza automática
        self._start_cleanup_thread()
    
    def _create_default_backend(self) -> CacheBackend:
        """Cria backend padrão baseado na configuração."""
        cache_enabled = get_config('performance.cache_enabled', True)
        if not cache_enabled:
            return MemoryBackend(max_size=0)  # Cache desabilitado
        
        # Por padrão usa SQLite para persistência
        return SQLiteBackend("cache.db")
    
    def _start_cleanup_thread(self):
        """Inicia thread de limpeza automática."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Limpa a cada 5 minutos
                    self.cleanup_expired()
                except Exception as e:
                    logger.error(f"Erro na limpeza do cache: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _generate_key(self, prompt: str, model: str, **kwargs) -> str:
        """Gera chave única para o cache."""
        # Normaliza entrada
        content = {
            'prompt': prompt.strip(),
            'model': model.strip(),
            **{k: v for k, v in kwargs.items() if v is not None}
        }
        
        # Gera hash
        content_str = json.dumps(content, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    @monitor_performance("cache_get")
    def get(self, prompt: str, model: str, **kwargs) -> Optional[str]:
        """Obtém resposta do cache."""
        if not get_config('performance.cache_enabled', True):
            return None
        
        key = self._generate_key(prompt, model, **kwargs)
        
        with self.lock:
            entry = self.backend.get(key)
            
            if entry is None:
                self.miss_count += 1
                logger.debug("Cache miss", key=key, prompt_length=len(prompt))
                return None
            
            # Verifica TTL
            if entry.ttl and time.time() > entry.ttl:
                self.backend.delete(key)
                self.miss_count += 1
                logger.debug("Cache expired", key=key)
                return None
            
            self.hit_count += 1
            logger.debug("Cache hit", key=key, access_count=entry.access_count)
            return entry.value
    
    @monitor_performance("cache_set")
    def set(self, prompt: str, model: str, response: str, ttl: Optional[float] = None, 
           tags: List[str] = None, **kwargs) -> bool:
        """Armazena resposta no cache."""
        if not get_config('performance.cache_enabled', True):
            return False
        
        if not response or len(response.strip()) == 0:
            return False
        
        key = self._generate_key(prompt, model, **kwargs)
        
        # Calcula TTL
        if ttl is None:
            ttl = time.time() + self.default_ttl
        elif ttl > 0:
            ttl = time.time() + ttl
        else:
            ttl = None  # Sem expiração
        
        entry = CacheEntry(
            key=key,
            value=response,
            timestamp=time.time(),
            ttl=ttl,
            tags=tags or [],
            metadata={
                'prompt_length': len(prompt),
                'response_length': len(response),
                'model': model,
                **kwargs
            }
        )
        
        with self.lock:
            success = self.backend.set(key, entry)
            if success:
                logger.debug("Cache stored", key=key, response_length=len(response))
            return success
    
    def invalidate(self, prompt: str = None, model: str = None, tags: List[str] = None, **kwargs) -> int:
        """Invalida entradas do cache."""
        count = 0
        
        with self.lock:
            if prompt and model:
                # Invalida entrada específica
                key = self._generate_key(prompt, model, **kwargs)
                if self.backend.delete(key):
                    count = 1
            else:
                # Invalida por tags ou outros critérios
                # Para SQLite backend, seria necessário implementar query por tags
                # Por simplicidade, implementação básica aqui
                if tags:
                    logger.warning("Invalidação por tags não implementada para este backend")
        
        logger.info("Cache invalidated", count=count)
        return count
    
    def clear(self) -> bool:
        """Limpa todo o cache."""
        with self.lock:
            success = self.backend.clear()
            if success:
                self.hit_count = 0
                self.miss_count = 0
                logger.info("Cache cleared")
            return success
    
    def cleanup_expired(self) -> int:
        """Remove entradas expiradas."""
        if isinstance(self.backend, SQLiteBackend):
            return self._cleanup_expired_sqlite()
        return 0
    
    def _cleanup_expired_sqlite(self) -> int:
        """Remove entradas expiradas do SQLite."""
        with self.lock:
            conn = sqlite3.connect(self.backend.db_path)
            try:
                current_time = time.time()
                cursor = conn.execute(
                    "DELETE FROM cache_entries WHERE ttl IS NOT NULL AND ttl < ?",
                    (current_time,)
                )
                conn.commit()
                count = cursor.rowcount
                
                if count > 0:
                    logger.info("Expired cache entries removed", count=count)
                
                return count
                
            except Exception as e:
                logger.error(f"Erro na limpeza de entradas expiradas: {e}")
                return 0
            finally:
                conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache."""
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
            
            return {
                'hit_count': self.hit_count,
                'miss_count': self.miss_count,
                'hit_rate': hit_rate,
                'total_entries': self.backend.size(),
                'backend_type': type(self.backend).__name__
            }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Obtém informações de uso de memória/espaço."""
        if isinstance(self.backend, SQLiteBackend):
            file_size = self.backend.db_path.stat().st_size if self.backend.db_path.exists() else 0
            return {
                'database_size_bytes': file_size,
                'database_size_mb': file_size / (1024 * 1024)
            }
        else:
            # Para backend em memória, estimativa simples
            return {
                'estimated_entries': self.backend.size(),
                'max_entries': getattr(self.backend, 'max_size', 0)
            }

# Instância global do cache
cache = IntelligentCache()

# Função helper para uso simples
@monitor_performance("cache_get_or_compute")
def cache_get_or_compute(prompt: str, model: str, compute_func, ttl: Optional[float] = None, **kwargs):
    """
    Obtém do cache ou computa se não existir.
    
    Args:
        prompt: Prompt para a IA
        model: Modelo a ser usado
        compute_func: Função para computar o resultado se não estiver no cache
        ttl: Tempo de vida no cache
        **kwargs: Argumentos adicionais para a chave do cache
    
    Returns:
        Resultado do cache ou computado
    """
    # Tenta obter do cache
    result = cache.get(prompt, model, **kwargs)
    
    if result is not None:
        logger.debug("Cache hit for prompt", prompt_length=len(prompt))
        return result
    
    # Computa resultado
    logger.debug("Cache miss, computing result", prompt_length=len(prompt))
    result = compute_func()
    
    # Armazena no cache
    if result:
        cache.set(prompt, model, result, ttl=ttl, **kwargs)
    
    return result

def get_cache() -> IntelligentCache:
    """Retorna a instância global do cache."""
    return cache
