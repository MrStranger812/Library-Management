import pytest
from flask import Flask
from app import get_app
from extensions import db
from models import init_models
import os

class TestConfig:
    """Test configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    
    # MySQL test database (if you prefer to test with MySQL)
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost/library_test'

@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for testing."""
    # Create test app with test configuration
    app = get_app(config=TestConfig)
    
    # Additional test configuration
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['TESTING'] = True
    
    # Create app context and initialize database
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize models (if needed)
        init_models()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def db_session(app):
    """Creates a new database session for a test."""
    with app.app_context():
        # Begin a transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use this connection
        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)
        
        # Save the original session
        old_session = db.session
        db.session = session
        
        yield session
        
        # Rollback transaction and restore original session
        transaction.rollback()
        connection.close()
        session.remove()
        db.session = old_session

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def auth_client(app, client, db_session):
    """A test client with authentication helpers."""
    from models.user import User
    
    class AuthClient:
        def __init__(self, client):
            self.client = client
            self.current_user = None
            
        def login(self, username='testuser', password='Test123!', create_user=True):
            """Login with a test user."""
            if create_user:
                # Create user if it doesn't exist
                user = User.query.filter_by(username=username).first()
                if not user:
                    user = User(
                        username=username,
                        email=f'{username}@example.com',
                        full_name='Test User',
                        role='member'
                    )
                    user.set_password(password)
                    db_session.add(user)
                    db_session.commit()
                self.current_user = user
            
            # Perform login
            return self.client.post('/login', data={
                'username': username,
                'password': password
            }, follow_redirects=True)
        
        def logout(self):
            """Logout the current user."""
            response = self.client.get('/logout', follow_redirects=True)
            self.current_user = None
            return response
        
        def login_as_admin(self):
            """Login as admin user."""
            return self.login('admin', 'admin123', create_user=False)
    
    return AuthClient(client)

@pytest.fixture
def sample_data(db_session):
    """Create sample data for tests."""
    from models.user import User
    from models.book import Book, Publisher, Category
    from models.tag import Tag
    
    # Create categories
    fiction = Category(name='Fiction', description='Fictional works')
    nonfiction = Category(name='Non-Fiction', description='Non-fictional works')
    db_session.add_all([fiction, nonfiction])
    
    # Create publishers
    pub1 = Publisher(name='Test Publisher 1', email='pub1@test.com')
    pub2 = Publisher(name='Test Publisher 2', email='pub2@test.com')
    db_session.add_all([pub1, pub2])
    
    # Create users
    admin = User(username='admin', email='admin@test.com', full_name='Admin User', role='admin')
    admin.set_password('admin123')
    
    user1 = User(username='user1', email='user1@test.com', full_name='User One', role='member')
    user1.set_password('Test123!')
    
    user2 = User(username='user2', email='user2@test.com', full_name='User Two', role='member')
    user2.set_password('Test123!')
    
    db_session.add_all([admin, user1, user2])
    db_session.commit()
    
    # Create books
    book1 = Book(
        isbn='1234567890',
        title='Python Programming',
        author='John Doe',
        publisher_id=pub1.publisher_id,
        category_id=fiction.category_id,
        publication_year=2023,
        total_copies=5
    )
    
    book2 = Book(
        isbn='0987654321',
        title='Data Science Basics',
        author='Jane Smith',
        publisher_id=pub2.publisher_id,
        category_id=nonfiction.category_id,
        publication_year=2023,
        total_copies=3
    )
    
    db_session.add_all([book1, book2])
    
    # Create tags
    tag1 = Tag(name='Popular', color='#FF0000')
    tag2 = Tag(name='New Arrival', color='#00FF00')
    db_session.add_all([tag1, tag2])
    
    db_session.commit()
    
    return {
        'users': {'admin': admin, 'user1': user1, 'user2': user2},
        'books': {'book1': book1, 'book2': book2},
        'categories': {'fiction': fiction, 'nonfiction': nonfiction},
        'publishers': {'pub1': pub1, 'pub2': pub2},
        'tags': {'popular': tag1, 'new': tag2}
    }