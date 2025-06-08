import pytest
from models.user import User
from datetime import datetime

def test_create_user(db_session):
    """Test user creation."""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='member'
    )
    user.set_password('testpass')  # Use set_password method
    db_session.add(user)
    db_session.commit()
    
    assert user.user_id is not None  # Changed from user.id
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.role == 'member'
    assert user.is_active is True

def test_user_password_hashing(db_session):
    """Test password hashing functionality."""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='member'
    )
    user.set_password('testpass')
    db_session.add(user)
    db_session.commit()
    
    assert user.verify_password('testpass') is True
    assert user.verify_password('wrongpass') is False

def test_user_email_validation(db_session):
    """Test user email validation."""
    # Test invalid email
    assert User.validate_email('invalid_email') is False
    assert User.validate_email('test@example.com') is True

def test_user_last_login(db_session):
    """Test last login tracking."""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='member'
    )
    user.set_password('testpass')
    db_session.add(user)
    db_session.commit()
    
    assert user.last_login is None
    
    user.update_last_login()
    db_session.commit()
    
    assert user.last_login is not None
    assert isinstance(user.last_login, datetime)

def test_user_deactivate_activate(db_session):
    """Test account activation/deactivation."""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='member'
    )
    user.set_password('testpass')
    db_session.add(user)
    db_session.commit()
    
    assert user.is_active is True
    
    # Deactivate user
    user.deactivate()
    assert user.is_active is False
    
    # Activate user
    user.activate()
    assert user.is_active is True