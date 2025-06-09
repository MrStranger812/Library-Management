from functools import wraps
from flask import request, abort, current_app, make_response
from utils.security import Security
from utils.logger import get_logger
import logging

logger = logging.getLogger(__name__)

def security_headers(response):
    """
    Add security headers to the response.
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

def validate_request():
    """
    Global middleware to validate request data.
    Only validates JSON requests that have a schema defined.
    """
    if request.is_json:
        try:
            # Only validate if there's a schema defined for this endpoint
            schema = getattr(request.endpoint, '_schema', None)
            if schema:
                from utils.validation import validate_json_schema
                validate_json_schema(schema)
        except Exception as e:
            abort(400, str(e))

def require_https():
    """
    Global middleware to require HTTPS.
    Only enforces HTTPS in production mode.
    """
    print("DEBUG require_https: is_secure:", request.is_secure, "debug:", current_app.debug, "testing:", current_app.testing)
    if not request.is_secure and not current_app.debug and not current_app.testing:
        abort(403, "HTTPS required")

def request_logger():
    """
    Log request details.
    """
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    if request.is_json:
        logger.info(f"JSON Body: {request.get_json()}")

def handle_cors():
    """
    Handle CORS headers.
    """
    if request.method == 'OPTIONS':
        response = current_app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response 