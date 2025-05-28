import secrets
import hashlib
from datetime import datetime, timedelta
from flask import request, abort
from utils.logger import get_logger

logger = get_logger('security')

class Security:
    @staticmethod
    def generate_token(length=32):
        """Generate a secure random token"""
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_data(data, salt=None):
        """
        Hash data with optional salt
        
        Args:
            data: Data to hash
            salt: Optional salt
        
        Returns:
            Tuple (hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Combine data and salt
        salted_data = f"{data}{salt}".encode('utf-8')
        
        # Create hash
        hash_obj = hashlib.sha256(salted_data)
        hash_hex = hash_obj.hexdigest()
        
        return hash_hex, salt
    
    @staticmethod
    def verify_hash(data, hash_value, salt):
        """
        Verify data against hash
        
        Args:
            data: Data to verify
            hash_value: Hash to verify against
            salt: Salt used for hashing
        
        Returns:
            Boolean indicating if data matches hash
        """
        # Combine data and salt
        salted_data = f"{data}{salt}".encode('utf-8')
        
        # Create hash
        hash_obj = hashlib.sha256(salted_data)
        computed_hash = hash_obj.hexdigest()
        
        return computed_hash == hash_value
    
    @staticmethod
    def rate_limit(key, limit=10, period=60):
        """
        Rate limiting function
        
        Args:
            key: Key to rate limit (e.g., IP address, user ID)
            limit: Maximum number of requests
            period: Time period in seconds
        
        Returns:
            Boolean indicating if request is allowed
        """
        from utils.cache import cache
        
        # Get current timestamp
        now = datetime.now().timestamp()
        
        # Get cache key
        cache_key = f"rate_limit:{key}"
        
        # Get existing timestamps from cache
        timestamps = cache.get(cache_key, [])
        
        # Filter out timestamps older than the period
        valid_timestamps = [ts for ts in timestamps if ts > now - period]
        
        # Check if limit is reached
        if len(valid_timestamps) >= limit:
            logger.warning(f"Rate limit exceeded for {key}")
            return False
        
        # Add current timestamp and update cache
        valid_timestamps.append(now)
        cache.set(cache_key, valid_timestamps, period)
        
        return True
    
    @staticmethod
    def check_ip_rate_limit(limit=10, period=60):
        """
        Check rate limit for current IP address
        
        Args:
            limit: Maximum number of requests
            period: Time period in seconds
        
        Returns:
            None, aborts with 429 if rate limit is exceeded
        """
        ip = request.remote_addr
        if not Security.rate_limit(ip, limit, period):
            logger.warning(f"IP rate limit exceeded: {ip}")
            abort(429, "Too many requests. Please try again later.")