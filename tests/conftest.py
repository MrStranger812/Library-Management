import pytest
from flask import Flask
from app import create_app
from extensions import db
import os
import tempfile
import shutil
from tests.test_config import TestConfig

@pytest.fixture(scope='session')
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestConfig)
    
    # Create a temporary directory for the test database
    db_fd, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Create the database and load test data
    with app.app_context():
        db.drop_all()  # Ensure clean state
        db.create_all()
        # Add any test data setup here
    
    yield app
    
    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()
    
    # Remove the temporary database file
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def db_session(app):
    """Creates a new database session for a test."""
    connection = db.engine.connect()
    transaction = connection.begin()
    
    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)
    
    db.session = session
    
    yield session
    
    transaction.rollback()
    connection.close()
    session.remove()

@pytest.fixture(scope='function')
def auth_client(client):
    """A test client with authentication."""
    def login(username, password):
        return client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    return login 