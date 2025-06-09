from flask import jsonify, render_template
from utils.logger import get_logger
from functools import wraps

logger = get_logger('app')

class ErrorHandler:
    @staticmethod
    def register_error_handlers(app):
        """Register error handlers for the Flask app"""
        
        @app.errorhandler(400)
        def bad_request(error):
            logger.error(f"400 Bad Request: {error}")
            if request_wants_json():
                return jsonify({"error": "Bad Request", "message": str(error)}), 400
            return render_template('errors/400.html', error=error), 400
        
        @app.errorhandler(401)
        def unauthorized(error):
            logger.error(f"401 Unauthorized: {error}")
            if request_wants_json():
                return jsonify({"error": "Unauthorized", "message": str(error)}), 401
            return render_template('errors/401.html', error=error), 401
        
        @app.errorhandler(403)
        def forbidden(error):
            logger.error(f"403 Forbidden: {error}")
            if request_wants_json():
                return jsonify({"error": "Forbidden", "message": str(error)}), 403
            return render_template('errors/403.html', error=error), 403
        
        @app.errorhandler(404)
        def not_found(error):
            logger.error(f"404 Not Found: {error}")
            if request_wants_json():
                return jsonify({"error": "Not Found", "message": str(error)}), 404
            return render_template('errors/404.html', error=error), 404
        
        @app.errorhandler(500)
        def server_error(error):
            logger.error(f"500 Server Error: {error}")
            if request_wants_json():
                return jsonify({"error": "Server Error", "message": str(error)}), 500
            return render_template('errors/500.html', error=error), 500
        
        @app.errorhandler(Exception)
        def handle_exception(error):
            logger.exception(f"Unhandled Exception: {error}")
            if request_wants_json():
                return jsonify({"error": "Server Error", "message": "An unexpected error occurred"}), 500
            return render_template('errors/500.html', error="An unexpected error occurred"), 500

def request_wants_json():
    """Check if the request wants a JSON response"""
    from flask import request
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    return (best == 'application/json' and
            request.accept_mimetypes[best] > request.accept_mimetypes['text/html'])

def handle_error(f):
    """Decorator to handle errors in route functions and return JSON responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in route: {e}")
            return jsonify({"error": "Server Error", "message": str(e)}), 500
    return decorated_function