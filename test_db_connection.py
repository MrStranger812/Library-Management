from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# Get database configuration
user = os.getenv('MYSQL_USER', 'root')
raw_password = os.getenv('MYSQL_PASSWORD', 'Qwaszxerdfcv56@')
password = urllib.parse.quote_plus(raw_password)
host = os.getenv('MYSQL_HOST', '127.0.0.1')
port = os.getenv('MYSQL_PORT', '3306')
db = os.getenv('MYSQL_DB', 'library_management')

# Print configuration
print(f"User: {user}")
print(f"Host: {host}")
print(f"Port: {port}")
print(f"Database: {db}")

# Create connection string using URL format
connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
print(f"\nConnection string (password masked): {connection_string.replace(password, '****')}")

try:
    # Create engine with explicit parameters
    engine = create_engine(
        connection_string,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            'connect_timeout': 10
        }
    )
    
    # Test connection
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DATABASE();"))
        print("\nConnected successfully!")
        print(f"Current database: {result.scalar()}")
except Exception as e:
    print(f"\nConnection failed: {str(e)}")
    print("\nTrying alternative connection method...")
    try:
        # Try alternative connection string format
        alt_connection_string = f"mysql+pymysql://{user}:{password}@localhost:{port}/{db}"
        engine = create_engine(alt_connection_string)
        with engine.connect() as connection:
            result = connection.execute(text("SELECT DATABASE();"))
            print("\nConnected successfully with alternative method!")
            print(f"Current database: {result.scalar()}")
    except Exception as e2:
        print(f"\nAlternative connection also failed: {str(e2)}") 