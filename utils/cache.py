import time
import threading
import functools

class Cache:
    _instance = None
    _cache = {}
    _expiry = {}
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
        return cls._instance
    
    def get(self, key, default=None):
        """Get value from cache"""
        with self._lock:
            # Check if key exists and not expired
            if key in self._cache and (key not in self._expiry or self._expiry[key] > time.time()):
                return self._cache[key]
            
            # Remove expired key
            if key in self._cache:
                del self._cache[key]
                if key in self._expiry:
                    del self._expiry[key]
            
            return default
    
    def set(self, key, value, ttl=None):
        """Set value in cache with optional TTL in seconds"""
        with self._lock:
            self._cache[key] = value
            if ttl is not None:
                self._expiry[key] = time.time() + ttl
    
    def delete(self, key):
        """Delete key from cache"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
    
    def clear(self):
        """Clear all cache"""
        with self._lock:
            self._cache.clear()
            self._expiry.clear()
    
    def cleanup(self):
        """Remove all expired keys"""
        with self._lock:
            current_time = time.time()
            expired_keys = [k for k, v in self._expiry.items() if v <= current_time]
            for key in expired_keys:
                if key in self._cache:
                    del self._cache[key]
                del self._expiry[key]

# Create a singleton instance
cache = Cache()

def cached(ttl=300):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_parts = [func.__name__]
            key_parts.extend([str(arg) for arg in args])
            key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator