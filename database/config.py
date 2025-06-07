import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'Qwaszxerdfcv56@'),
    'database': os.getenv('MYSQL_DB', 'library_management'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'

# Database pool configuration
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
    'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
    'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
    'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 5))
} 