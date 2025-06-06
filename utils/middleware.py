from functools import wraps
from flask import request, abort, current_app
from utils.security import Security
from utils.logger import get_logger

logger = get_logger('middleware')

def security_headers():
    """
    Middleware to add security headers to all responses
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)
            
            # Add security headers
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
            
            return response
        return wrapped
    return decorator

def validate_request():
    """
    Middleware to validate incoming requests
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Check content type for POST/PUT requests
            if request.method in ['POST', 'PUT']:
                if not request.is_json and request.headers.get('Content-Type') == 'application/json':
                    abort(400, "Content-Type must be application/json")
            
            # Validate request size
            if request.content_length and request.content_length > current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024):
                abort(413, "Request entity too large")
            
            # Check for common attack patterns
            for key, value in request.args.items():
                if any(pattern in value.lower() for pattern in ['<script', 'javascript:', 'onerror=', 'onload=']):
                    logger.warning(f"Potential XSS attack detected in query parameter: {key}")
                    abort(400, "Invalid request parameters")
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def require_https():
    """
    Middleware to require HTTPS
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not request.is_secure and not current_app.debug:
                abort(403, "HTTPS required")
            return f(*args, **kwargs)
        return wrapped
    return decorator

def validate_json_schema(schema):
    """
    Middleware to validate JSON request body against a schema
    
    Args:
        schema: JSON schema to validate against
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not request.is_json:
                abort(400, "Content-Type must be application/json")
            
            try:
                from jsonschema import validate
                validate(instance=request.get_json(), schema=schema)
            except Exception as e:
                logger.warning(f"JSON validation error: {str(e)}")
                abort(400, f"Invalid request body: {str(e)}")
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

def log_request():
    """
    Middleware to log incoming requests
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")
            return f(*args, **kwargs)
        return wrapped
    return decorator

def handle_cors():
    """
    Middleware to handle CORS
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            response = f(*args, **kwargs)
            
            # Add CORS headers
            response.headers['Access-Control-Allow-Origin'] = current_app.config.get('CORS_ORIGINS', '*')
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
            
            return response
        return wrapped
    return decorator 