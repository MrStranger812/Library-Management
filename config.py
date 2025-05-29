import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or 'your_password'
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'library_management'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_CHARSET = 'utf8mb4'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # Application Configuration
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't')
    TESTING = False
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