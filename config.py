import os
from dotenv import load_dotenv
import logging
import urllib.parse

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug: Print environment variables
logger.debug(f"MYSQL_USER: {os.getenv('MYSQL_USER')}")
logger.debug(f"MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
logger.debug(f"MYSQL_PORT: {os.getenv('MYSQL_PORT')}")
logger.debug(f"MYSQL_DB: {os.getenv('MYSQL_DB')}")
# Don't log the password for security reasons

# Update SQLALCHEMY_DATABASE_URI to use environment variables for MySQL credentials
user = os.getenv('MYSQL_USER', 'root')
raw_password = os.getenv('MYSQL_PASSWORD', 'Qwaszxerdfcv56@')
password = urllib.parse.quote_plus(raw_password)
host = os.getenv('MYSQL_HOST', '127.0.0.1')
port = os.getenv('MYSQL_PORT', '3306')
db = os.getenv('MYSQL_DB', 'library_management')

# Debug print each component
logger.debug(f"Database components:")
logger.debug(f"User: {user}")
logger.debug(f"Host: {host}")
logger.debug(f"Port: {port}")
logger.debug(f"Database: {db}")

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"

# Debug print the full URI (with password masked)
masked_uri = SQLALCHEMY_DATABASE_URI.replace(password, '****')
logger.debug(f"Full Database URI: {masked_uri}")

# Add SQLAlchemy specific configurations
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

logger.debug(f"Database URI: {SQLALCHEMY_DATABASE_URI.replace(os.getenv('MYSQL_PASSWORD', ''), '****')}")

class Config:
    # Database Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'Qwaszxerdfcv56@'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'library_management'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{urllib.parse.quote_plus(MYSQL_PASSWORD)}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # Application Configuration
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'csv', 'xlsx'}
    
    # Email Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # Redis Configuration (for caching and session storage)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Celery Configuration (for background tasks)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL
    
    # Library Specific Configuration
    DEFAULT_LOAN_DURATION = int(os.environ.get('DEFAULT_LOAN_DURATION', 14))
    DEFAULT_FINE_RATE = float(os.environ.get('DEFAULT_FINE_RATE', 0.50))
    MAX_RENEWALS = int(os.environ.get('MAX_RENEWALS', 2))
    RESERVATION_EXPIRY_DAYS = int(os.environ.get('RESERVATION_EXPIRY_DAYS', 7))
    OVERDUE_NOTIFICATION_DAYS = int(os.environ.get('OVERDUE_NOTIFICATION_DAYS', 3))
    
    # Pagination Configuration
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 10))
    MAX_ITEMS_PER_PAGE = int(os.environ.get('MAX_ITEMS_PER_PAGE', 100))
    
    # Security Configuration
    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Logging Configuration
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT', 'False').lower() in ('true', '1', 't')
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # API Configuration
    API_VERSION = 'v1'
    API_TITLE = 'Library Management System API'
    API_DESCRIPTION = 'RESTful API for Library Management System'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_DB = os.environ.get('DEV_DATABASE_URL') or Config.MYSQL_DB + '_dev'

class TestingConfig(Config):
    TESTING = True
    MYSQL_DB = os.environ.get('TEST_DATABASE_URL') or Config.MYSQL_DB + '_test'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log to syslog in production
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}