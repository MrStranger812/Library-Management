from flask import Flask
from database import config as db_config
from extensions import db, bcrypt, login_manager, jwt
from utils.security import Security
from utils.middleware import security_headers, request_logger, require_https, handle_cors
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

# Import models in the correct order to avoid circular dependencies
from models import db, init_models
from models.user import User
from models.book import Book
from models.author import Author
from models.publisher import Publisher
from models.category import Category
from models.book_copy import BookCopy
from models.borrowing import Borrowing
from models.membership import MembershipType, UserMembership
from models.library_branch import LibraryBranch
from models.library_event import LibraryEvent
from models.event_registration import EventRegistration
from models.book_review import BookReview
from models.tag import Tag, BookTag
from models.notification import Notification, AuditLog, UserPreference
from models.reports import Reports
from models.fine import Fine
from models.fine_payment import FinePayment

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Ensure SQLAlchemy configuration is set
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = config_class.SQLALCHEMY_DATABASE_URI
    
    # Ensure debug mode is enabled in development
    app.config['DEBUG'] = True
    app.debug = True
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    CORS(app)
    jwt.init_app(app)
    
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
    from routes.reports import reports_bp
    from routes.main import main
    
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
    app.register_blueprint(reports_bp)
    app.register_blueprint(main)
    
    # Register error handlers
    from utils.error_handler import ErrorHandler
    ErrorHandler.register_error_handlers(app)
    
    # Register middleware
    app.after_request(security_headers)
    app.before_request(request_logger)
    app.before_request(require_https)
    app.before_request(handle_cors)
    app.before_request(Security.check_ip_rate_limit)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    
    # Create database tables
    with app.app_context():
        init_models()
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(int(user_id))
    
    return app 