from flask import Flask
from database import config as db_config
from extensions import db, bcrypt, login_manager
from utils.security import Security
from utils.middleware import security_headers, validate_request, require_https, validate_json_schema, log_request, handle_cors

def create_app(config=None):
    app = Flask(__name__)
    
    # Load default configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = db_config.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = db_config.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_ECHO'] = db_config.SQLALCHEMY_ECHO
    app.config.update(db_config.SQLALCHEMY_ENGINE_OPTIONS)
    
    # Load custom configuration if provided
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.users import users_bp
    from routes.borrowings import borrowings_bp
    from routes.authors import authors_bp
    from routes.events import events_bp
    from routes.preferences import preferences_bp
    from routes.tags import tags_bp
    from routes.fines import fines_bp
    from routes.audit import audit_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(borrowings_bp)
    app.register_blueprint(authors_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(preferences_bp)
    app.register_blueprint(tags_bp)
    app.register_blueprint(fines_bp)
    app.register_blueprint(audit_bp)
    
    # Register error handlers
    from utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Register middleware
    app.before_request(security_headers)
    app.before_request(validate_request)
    app.before_request(require_https)
    app.before_request(handle_cors)
    app.before_request(Security.check_ip_rate_limit)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 