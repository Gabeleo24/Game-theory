"""
Cache manager for API responses to avoid repeated requests and respect rate limits.
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
import logging

from ..utils.config import Config


class CacheManager:
    """Manages caching of API responses to JSON files."""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory for cache files. If None, uses config default.
        """
        self.config = Config()
        self.cache_dir = cache_dir or self.config.get('data_collection.cache_directory', 'data/raw')
        self.cache_duration_hours = self.config.get('api_football.cache_duration_hours', 24)
        self.logger = logging.getLogger(__name__)
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_filename(self, key: str) -> str:
        """
        Generate a cache filename from a key.
        
        Args:
            key: Cache key
            
        Returns:
            Cache filename
        """
        # Create a hash of the key for consistent filename
        key_hash = hashlib.md5(str(key).encode()).hexdigest()
        return os.path.join(self.cache_dir, f"cache_{key_hash}.json")
    
    def _is_cache_valid(self, filepath: str) -> bool:
        """
        Check if cache file is still valid based on age.
        
        Args:
            filepath: Path to cache file
            
        Returns:
            True if cache is valid, False otherwise
        """
        if not os.path.exists(filepath):
            return False
        
        # Check file age
        file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        expiry_time = datetime.now() - timedelta(hours=self.cache_duration_hours)
        
        return file_time > expiry_time
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get data from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if available and valid, None otherwise
        """
        filepath = self._get_cache_filename(key)
        
        if not self._is_cache_valid(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"Cache hit for key: {key}")
            return data
            
        except (json.JSONDecodeError, FileNotFoundError, IOError) as e:
            self.logger.warning(f"Error reading cache file {filepath}: {e}")
            return None
    
    def set(self, key: str, data: Dict[str, Any]) -> None:
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        filepath = self._get_cache_filename(key)
        
        try:
            # Add metadata to cached data
            cache_data = {
                'cached_at': datetime.now().isoformat(),
                'cache_key': key,
                'data': data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Data cached for key: {key}")
            
        except (IOError, TypeError) as e:
            self.logger.error(f"Error writing cache file {filepath}: {e}")
    
    def clear(self, key: Optional[str] = None) -> None:
        """
        Clear cache data.
        
        Args:
            key: Specific key to clear. If None, clears all cache.
        """
        if key:
            filepath = self._get_cache_filename(key)
            if os.path.exists(filepath):
                os.remove(filepath)
                self.logger.info(f"Cleared cache for key: {key}")
        else:
            # Clear all cache files
            for filename in os.listdir(self.cache_dir):
                if filename.startswith('cache_') and filename.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, filename)
                    os.remove(filepath)
            
            self.logger.info("Cleared all cache files")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached data.
        
        Returns:
            Cache information including file count and total size
        """
        cache_files = []
        total_size = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.startswith('cache_') and filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                file_size = os.path.getsize(filepath)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                cache_files.append({
                    'filename': filename,
                    'size_bytes': file_size,
                    'created_at': file_time.isoformat(),
                    'is_valid': self._is_cache_valid(filepath)
                })
                
                total_size += file_size
        
        return {
            'cache_directory': self.cache_dir,
            'total_files': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_duration_hours': self.cache_duration_hours,
            'files': cache_files
        }
    
    def cleanup_expired(self) -> int:
        """
        Remove expired cache files.
        
        Returns:
            Number of files removed
        """
        removed_count = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.startswith('cache_') and filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                
                if not self._is_cache_valid(filepath):
                    os.remove(filepath)
                    removed_count += 1
        
        self.logger.info(f"Removed {removed_count} expired cache files")
        return removed_count
