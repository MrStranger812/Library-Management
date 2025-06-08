import os
from datetime import timedelta
import tempfile

class TestConfig:
    """Test configuration for the application."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Password requirements
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Test user credentials
    TEST_USER_USERNAME = 'testuser'
    TEST_USER_PASSWORD = 'Test123!'
    TEST_USER_EMAIL = 'test@example.com'
    TEST_USER_FULL_NAME = 'Test User'
    
    # Test admin credentials
    TEST_ADMIN_USERNAME = 'admin'
    TEST_ADMIN_PASSWORD = 'Admin123!'
    TEST_ADMIN_EMAIL = 'admin@example.com'
    TEST_ADMIN_FULL_NAME = 'Admin User'
    
    MAIL_SUPPRESS_SEND = True
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'test@example.com'
    UPLOAD_FOLDER = tempfile.mkdtemp()
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 