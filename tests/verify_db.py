import os
import sys

# Add project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask
from extensions import db
from models import init_models
from test_config import TestConfig
from sqlalchemy import text, inspect

def create_test_app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    # Initialize extensions
    db.init_app(app)
    
    return app

def verify_database():
    """Verify database connection and schema."""
    print("🔍 Verifying database connection and schema...")
    
    # Create test app
    app = create_test_app()
    
    with app.app_context():
        try:
            # Test database connection
            db.engine.connect()
            print("✅ Database connection successful")
            
            # Drop all tables and indexes
            print("Cleaning up existing database...")
            db.drop_all()
            
            # Create tables in correct order
            print("Creating database tables...")
            
            # Get all models
            inspector = inspect(db.engine)
            metadata = db.metadata
            
            # Create tables in dependency order
            for table in metadata.sorted_tables:
                if not inspector.has_table(table.name):
                    print(f"Creating table: {table.name}")
                    table.create(db.engine)
            
            print("✅ Database tables created")
            
            # Initialize models
            print("Initializing models...")
            init_models()
            print("✅ Models initialized")
            
            # Verify tables exist
            tables = inspector.get_table_names()
            required_tables = [
                'users', 'books', 'publishers', 'categories',
                'borrowings', 'fines', 'tags', 'book_tags',
                'library_events', 'event_registrations'
            ]
            
            missing_tables = [table for table in required_tables if table not in tables]
            if missing_tables:
                print(f"❌ Missing tables: {', '.join(missing_tables)}")
                return False
            
            print("✅ All required tables exist")
            
            # Verify indexes
            print("\nVerifying indexes...")
            for table_name in tables:
                indexes = inspector.get_indexes(table_name)
                print(f"Table {table_name} has {len(indexes)} indexes")
            
            return True
            
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            return False
        finally:
            # Cleanup
            try:
                db.session.remove()
                db.drop_all()
            except Exception as e:
                print(f"Warning: Error during cleanup: {str(e)}")

if __name__ == "__main__":
    success = verify_database()
    sys.exit(0 if success else 1) 