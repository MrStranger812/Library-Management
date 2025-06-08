# test_minimal.py - A minimal test that should work
"""
Minimal working test to verify test setup is correct.
Run with: pytest test_minimal.py -v
"""

import pytest
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from flask import Flask
from extensions import db
from models.user import User
from models.book import Book, Publisher, Category

# Test configuration
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-key'
    WTF_CSRF_ENABLED = False

@pytest.fixture(scope='module')
def test_app():
    """Create test application."""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    # Initialize extensions
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope='function')
def session(test_app):
    """Create database session for tests."""
    with test_app.app_context():
        yield db.session
        db.session.rollback()

def test_database_connection(session):
    """Test that database connection works."""
    # This test just verifies we can connect
    assert session is not None
    print("✅ Database connection successful")

def test_create_simple_user(session):
    """Test creating a simple user."""
    # Create user with minimal required fields
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='member'
    )
    user.set_password('Test123!')
    
    session.add(user)
    session.commit()
    
    # Verify user was created
    assert user.user_id is not None
    assert user.username == 'testuser'
    print(f"✅ User created with ID: {user.user_id}")

def test_create_simple_book(session):
    """Test creating a simple book."""
    # Create publisher first (if required by schema)
    publisher = Publisher(name='Test Publisher')
    session.add(publisher)
    session.commit()
    
    # Create category (if required by schema)
    category = Category(name='Test Category')
    session.add(category)
    session.commit()
    
    # Create book
    book = Book(
        isbn='1234567890',
        title='Test Book',
        author='Test Author',  # Required by schema
        publisher_id=publisher.publisher_id,
        category_id=category.category_id,
        total_copies=1
    )
    
    session.add(book)
    session.commit()
    
    # Verify book was created
    assert book.book_id is not None
    assert book.title == 'Test Book'
    assert book.copies_available == 1  # Should match total_copies
    print(f"✅ Book created with ID: {book.book_id}")

def test_query_data(session):
    """Test querying data from database."""
    # Create test data
    user = User(
        username='querytest',
        email='query@test.com',
        full_name='Query Test',
        role='member'
    )
    user.set_password('Test123!')
    session.add(user)
    session.commit()
    
    # Query the data
    found_user = User.query.filter_by(username='querytest').first()
    
    assert found_user is not None
    assert found_user.email == 'query@test.com'
    print("✅ Query successful")

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, '-v'])