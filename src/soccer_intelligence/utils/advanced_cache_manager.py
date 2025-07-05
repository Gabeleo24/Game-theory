"""
Advanced Cache Manager for ADS599 Capstone Soccer Intelligence System
Implements multi-level caching with Redis, memory-mapped files, and intelligent invalidation
for optimized performance with the 67 UEFA Champions League teams dataset.
"""

import redis
import pickle
import json
import hashlib
import time
import mmap
import os
import gc
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import wraps
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import pandas as pd
import numpy as np

try:
    import lz4.frame as lz4
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from .config import Config
from .logger import get_logger


@dataclass
class CacheStats:
    """Cache performance statistics."""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    memory_usage_mb: float = 0.0
    redis_memory_mb: float = 0.0
    file_cache_size_mb: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / max(total, 1)
    
    @property
    def total_memory_mb(self) -> float:
        return self.memory_usage_mb + self.redis_memory_mb + self.file_cache_size_mb


class AdvancedCacheManager:
    """
    Multi-level cache manager with Redis, memory, and file-based caching.
    Optimized for soccer intelligence data processing workflows.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the advanced cache manager."""
        self.config = config or Config()
        self.logger = get_logger(__name__)
        
        # Cache configuration
        self.cache_config = self.config.get('performance.caching', {})
        
        # Redis configuration
        self.redis_config = self.cache_config.get('redis', {})
        self.redis_host = os.getenv('REDIS_HOST', 'redis')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_password = os.getenv('REDIS_PASSWORD', 'redispass123')
        self.redis_db = 0
        
        # Cache strategy configuration
        self.strategy_config = self.cache_config.get('strategy', {})
        self.default_ttl = self.strategy_config.get('default_ttl', 3600)
        self.compression_enabled = self.strategy_config.get('compression', True)
        self.serialization_method = self.strategy_config.get('serialization', 'pickle')
        
        # Cache levels configuration
        self.levels_config = self.cache_config.get('levels', {})
        self.l1_cache_size = self.levels_config.get('l1_memory_cache_size', 1000)
        self.l2_redis_enabled = self.levels_config.get('l2_redis_cache', True)
        self.l3_file_enabled = self.levels_config.get('l3_file_cache', True)
        self.cache_warming_enabled = self.levels_config.get('cache_warming', True)
        
        # File cache configuration
        self.file_cache_dir = Path(self.config.get('data_collection.cache_directory', 'data/cache'))
        self.file_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache components
        self._init_redis_connection()
        self._init_memory_cache()
        self._init_file_cache()
        
        # Statistics and monitoring
        self.stats = CacheStats()
        self._stats_lock = threading.Lock()
        
        # Memory monitoring
        self.process = psutil.Process()
        self.memory_threshold_mb = 1024  # 1GB threshold
        
        self.logger.info(f"Advanced cache manager initialized with L1={self.l1_cache_size}, "
                        f"L2_Redis={self.l2_redis_enabled}, L3_File={self.l3_file_enabled}")
    
    def _init_redis_connection(self) -> None:
        """Initialize Redis connection with connection pooling."""
        if not self.l2_redis_enabled:
            self.redis_client = None
            return
        
        try:
            pool = redis.ConnectionPool(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=self.redis_db,
                max_connections=self.redis_config.get('max_connections', 50),
                socket_timeout=self.redis_config.get('socket_timeout', 30),
                socket_connect_timeout=self.redis_config.get('socket_connect_timeout', 30),
                socket_keepalive=self.redis_config.get('socket_keepalive', True),
                decode_responses=False  # We handle binary data
            )
            
            self.redis_client = redis.Redis(connection_pool=pool)
            
            # Test connection
            self.redis_client.ping()
            self.logger.info("Redis connection established successfully")
            
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}. Disabling Redis cache.")
            self.redis_client = None
            self.l2_redis_enabled = False
    
    def _init_memory_cache(self) -> None:
        """Initialize in-memory LRU cache."""
        self.memory_cache = {}
        self.memory_cache_order = []
        self.memory_cache_lock = threading.Lock()
    
    def _init_file_cache(self) -> None:
        """Initialize file-based cache."""
        self.file_cache_lock = threading.Lock()
        
        # Create subdirectories for different data types
        (self.file_cache_dir / 'players').mkdir(exist_ok=True)
        (self.file_cache_dir / 'teams').mkdir(exist_ok=True)
        (self.file_cache_dir / 'matches').mkdir(exist_ok=True)
        (self.file_cache_dir / 'analysis').mkdir(exist_ok=True)
        (self.file_cache_dir / 'shapley').mkdir(exist_ok=True)
    
    def _generate_cache_key(self, key: str, namespace: str = 'default') -> str:
        """Generate a standardized cache key."""
        combined_key = f"{namespace}:{key}"
        return hashlib.md5(combined_key.encode()).hexdigest()
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data with optional compression."""
        if self.serialization_method == 'json':
            serialized = json.dumps(data, default=str).encode()
        else:  # pickle
            serialized = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        
        if self.compression_enabled and LZ4_AVAILABLE:
            return lz4.compress(serialized)
        elif self.compression_enabled and JOBLIB_AVAILABLE:
            return joblib.dump(data, None, compress=3)[0]
        else:
            return serialized
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data with optional decompression."""
        try:
            if self.compression_enabled and LZ4_AVAILABLE:
                decompressed = lz4.decompress(data)
            elif self.compression_enabled and JOBLIB_AVAILABLE:
                return joblib.load([data])[0]
            else:
                decompressed = data
            
            if self.serialization_method == 'json':
                return json.loads(decompressed.decode())
            else:  # pickle
                return pickle.loads(decompressed)
                
        except Exception as e:
            self.logger.error(f"Error deserializing data: {e}")
            return None
    
    def _manage_memory_cache(self) -> None:
        """Manage memory cache size using LRU eviction."""
        with self.memory_cache_lock:
            while len(self.memory_cache) > self.l1_cache_size:
                # Remove least recently used item
                oldest_key = self.memory_cache_order.pop(0)
                if oldest_key in self.memory_cache:
                    del self.memory_cache[oldest_key]
    
    def _update_memory_cache_order(self, key: str) -> None:
        """Update the order for LRU management."""
        with self.memory_cache_lock:
            if key in self.memory_cache_order:
                self.memory_cache_order.remove(key)
            self.memory_cache_order.append(key)
    
    def _get_from_memory_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from L1 memory cache."""
        with self.memory_cache_lock:
            if cache_key in self.memory_cache:
                self._update_memory_cache_order(cache_key)
                return self.memory_cache[cache_key]
        return None
    
    def _set_to_memory_cache(self, cache_key: str, data: Any) -> None:
        """Set data to L1 memory cache."""
        with self.memory_cache_lock:
            self.memory_cache[cache_key] = data
            self._update_memory_cache_order(cache_key)
            self._manage_memory_cache()
    
    def _get_from_redis_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from L2 Redis cache."""
        if not self.l2_redis_enabled or not self.redis_client:
            return None
        
        try:
            data = self.redis_client.get(cache_key)
            if data:
                return self._deserialize_data(data)
        except Exception as e:
            self.logger.warning(f"Redis get error for key {cache_key}: {e}")
        
        return None
    
    def _set_to_redis_cache(self, cache_key: str, data: Any, ttl: Optional[int] = None) -> None:
        """Set data to L2 Redis cache."""
        if not self.l2_redis_enabled or not self.redis_client:
            return
        
        try:
            serialized_data = self._serialize_data(data)
            ttl = ttl or self.default_ttl
            self.redis_client.setex(cache_key, ttl, serialized_data)
        except Exception as e:
            self.logger.warning(f"Redis set error for key {cache_key}: {e}")
    
    def _get_file_cache_path(self, cache_key: str, namespace: str = 'default') -> Path:
        """Get file path for cache key."""
        return self.file_cache_dir / namespace / f"{cache_key}.cache"
    
    def _get_from_file_cache(self, cache_key: str, namespace: str = 'default') -> Optional[Any]:
        """Get data from L3 file cache."""
        if not self.l3_file_enabled:
            return None
        
        cache_file = self._get_file_cache_path(cache_key, namespace)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                data = f.read()
            return self._deserialize_data(data)
        except Exception as e:
            self.logger.warning(f"File cache read error for {cache_file}: {e}")
            return None
    
    def _set_to_file_cache(self, cache_key: str, data: Any, namespace: str = 'default') -> None:
        """Set data to L3 file cache."""
        if not self.l3_file_enabled:
            return
        
        cache_file = self._get_file_cache_path(cache_key, namespace)
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with self.file_cache_lock:
                serialized_data = self._serialize_data(data)
                with open(cache_file, 'wb') as f:
                    f.write(serialized_data)
        except Exception as e:
            self.logger.warning(f"File cache write error for {cache_file}: {e}")
    
    def get(self, key: str, namespace: str = 'default') -> Optional[Any]:
        """
        Get data from multi-level cache (L1 -> L2 -> L3).
        
        Args:
            key: Cache key
            namespace: Cache namespace for organization
            
        Returns:
            Cached data if found, None otherwise
        """
        cache_key = self._generate_cache_key(key, namespace)
        
        # Try L1 memory cache first
        data = self._get_from_memory_cache(cache_key)
        if data is not None:
            with self._stats_lock:
                self.stats.hits += 1
            self.logger.debug(f"L1 cache hit for key: {key}")
            return data
        
        # Try L2 Redis cache
        data = self._get_from_redis_cache(cache_key)
        if data is not None:
            # Promote to L1 cache
            self._set_to_memory_cache(cache_key, data)
            with self._stats_lock:
                self.stats.hits += 1
            self.logger.debug(f"L2 cache hit for key: {key}")
            return data
        
        # Try L3 file cache
        data = self._get_from_file_cache(cache_key, namespace)
        if data is not None:
            # Promote to L1 and L2 caches
            self._set_to_memory_cache(cache_key, data)
            self._set_to_redis_cache(cache_key, data)
            with self._stats_lock:
                self.stats.hits += 1
            self.logger.debug(f"L3 cache hit for key: {key}")
            return data
        
        # Cache miss
        with self._stats_lock:
            self.stats.misses += 1
        self.logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None, 
           namespace: str = 'default') -> None:
        """
        Set data to all cache levels.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
            namespace: Cache namespace for organization
        """
        cache_key = self._generate_cache_key(key, namespace)
        
        # Set to all cache levels
        self._set_to_memory_cache(cache_key, data)
        self._set_to_redis_cache(cache_key, data, ttl)
        self._set_to_file_cache(cache_key, data, namespace)
        
        with self._stats_lock:
            self.stats.sets += 1
        
        self.logger.debug(f"Data cached for key: {key}")
    
    def delete(self, key: str, namespace: str = 'default') -> None:
        """
        Delete data from all cache levels.
        
        Args:
            key: Cache key
            namespace: Cache namespace for organization
        """
        cache_key = self._generate_cache_key(key, namespace)
        
        # Delete from L1 memory cache
        with self.memory_cache_lock:
            if cache_key in self.memory_cache:
                del self.memory_cache[cache_key]
            if cache_key in self.memory_cache_order:
                self.memory_cache_order.remove(cache_key)
        
        # Delete from L2 Redis cache
        if self.l2_redis_enabled and self.redis_client:
            try:
                self.redis_client.delete(cache_key)
            except Exception as e:
                self.logger.warning(f"Redis delete error for key {cache_key}: {e}")
        
        # Delete from L3 file cache
        if self.l3_file_enabled:
            cache_file = self._get_file_cache_path(cache_key, namespace)
            if cache_file.exists():
                try:
                    cache_file.unlink()
                except Exception as e:
                    self.logger.warning(f"File cache delete error for {cache_file}: {e}")
        
        with self._stats_lock:
            self.stats.deletes += 1
        
        self.logger.debug(f"Cache entry deleted for key: {key}")
    
    def clear_namespace(self, namespace: str) -> None:
        """Clear all cache entries in a specific namespace."""
        # Clear file cache for namespace
        if self.l3_file_enabled:
            namespace_dir = self.file_cache_dir / namespace
            if namespace_dir.exists():
                for cache_file in namespace_dir.glob('*.cache'):
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        self.logger.warning(f"Error deleting cache file {cache_file}: {e}")
        
        # Clear Redis cache for namespace (pattern-based deletion)
        if self.l2_redis_enabled and self.redis_client:
            try:
                pattern = f"*{namespace}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except Exception as e:
                self.logger.warning(f"Redis namespace clear error: {e}")
        
        # Clear memory cache (partial - we can't easily filter by namespace)
        # This is a limitation of the current implementation
        
        self.logger.info(f"Cleared cache namespace: {namespace}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self._stats_lock:
            stats_dict = asdict(self.stats)
        
        # Add current memory usage
        stats_dict['current_memory_mb'] = self.process.memory_info().rss / (1024 ** 2)
        
        # Add Redis memory usage if available
        if self.l2_redis_enabled and self.redis_client:
            try:
                redis_info = self.redis_client.info('memory')
                stats_dict['redis_memory_mb'] = redis_info.get('used_memory', 0) / (1024 ** 2)
            except Exception:
                stats_dict['redis_memory_mb'] = 0
        
        # Add file cache size
        if self.l3_file_enabled:
            total_size = sum(f.stat().st_size for f in self.file_cache_dir.rglob('*.cache'))
            stats_dict['file_cache_size_mb'] = total_size / (1024 ** 2)
        
        return stats_dict
