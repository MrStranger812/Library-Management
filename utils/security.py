import secrets
import hashlib
import re
from datetime import datetime, timedelta
from flask import request, abort, current_app
from utils.logger import get_logger
from utils.cache import cache

logger = get_logger('security')

class Security:
    # Password requirements
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Account lockout settings
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 30  # minutes
    
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
    def validate_password(password):
        """
        Validate password against security requirements
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple (bool, str) - (is_valid, error_message)
        """
        if len(password) < Security.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {Security.PASSWORD_MIN_LENGTH} characters long"
        
        if Security.PASSWORD_REQUIRE_UPPER and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if Security.PASSWORD_REQUIRE_LOWER and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if Security.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if Security.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def check_login_attempts(username):
        """
        Check if user account is locked due to too many failed login attempts
        
        Args:
            username: Username to check
        
        Returns:
            Tuple (bool, str) - (is_locked, message)
        """
        cache_key = f"login_attempts:{username}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= Security.MAX_LOGIN_ATTEMPTS:
            lockout_key = f"account_locked:{username}"
            lockout_time = cache.get(lockout_key)
            
            if lockout_time:
                remaining_time = (lockout_time - datetime.now()).total_seconds() / 60
                if remaining_time > 0:
                    return True, f"Account is locked. Try again in {int(remaining_time)} minutes"
                else:
                    # Reset attempts after lockout period
                    cache.delete(cache_key)
                    cache.delete(lockout_key)
                    return False, ""
            
            # Set lockout
            cache.set(lockout_key, datetime.now() + timedelta(minutes=Security.LOCKOUT_DURATION))
            return True, f"Account is locked for {Security.LOCKOUT_DURATION} minutes"
        
        return False, ""
    
    @staticmethod
    def record_login_attempt(username, success):
        """
        Record a login attempt
        
        Args:
            username: Username of the attempt
            success: Whether the attempt was successful
        """
        cache_key = f"login_attempts:{username}"
        
        if success:
            cache.delete(cache_key)
            cache.delete(f"account_locked:{username}")
        else:
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, timeout=3600)  # Store for 1 hour
    
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
    
    @staticmethod
    def validate_api_key(api_key):
        """
        Validate API key
        
        Args:
            api_key: API key to validate
        
        Returns:
            Boolean indicating if API key is valid
        """
        # Get API keys from configuration
        valid_keys = current_app.config.get('API_KEYS', [])
        return api_key in valid_keys
    
    @staticmethod
    def require_api_key():
        """
        Decorator to require API key for endpoints
        
        Returns:
            Decorator function
        """
        def decorator(f):
            def wrapped(*args, **kwargs):
                api_key = request.headers.get('X-API-Key')
                if not api_key or not Security.validate_api_key(api_key):
                    abort(401, "Invalid or missing API key")
                return f(*args, **kwargs)
            return wrapped
        return decorator