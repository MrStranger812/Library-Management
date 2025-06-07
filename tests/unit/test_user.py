import pytest
from models.user import User
from werkzeug.security import check_password_hash
from datetime import datetime

def test_create_user(db_session):
    """Test user creation."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpass',
        full_name='Test User',
        role='member'
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.user_id is not None
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.role == 'member'
    assert user.is_active is True

def test_user_password_hashing(db_session):
    """Test password hashing functionality."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpass',
        full_name='Test User',
        role='member'
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.verify_password('testpass') is True
    assert user.verify_password('wrongpass') is False

def test_user_role_validation(db_session):
    """Test user role validation."""
    with pytest.raises(ValueError):
        User(
            username='testuser',
            email='test@example.com',
            password='testpass',
            full_name='Test User',
            role='invalid_role'
        )

def test_user_email_validation(db_session):
    """Test user email validation."""
    with pytest.raises(ValueError):
        User(
            username='testuser',
            email='invalid_email',
            password='testpass',
            full_name='Test User',
            role='member'
        )

def test_user_username_validation(db_session):
    """Test username validation."""
    with pytest.raises(ValueError):
        User(
            username='a',  # Too short
            email='test@example.com',
            password='testpass',
            full_name='Test User',
            role='member'
        )

def test_user_last_login(db_session):
    """Test last login tracking."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpass',
        full_name='Test User',
        role='member'
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.last_login is None
    
    user.last_login = datetime.utcnow()
    db_session.commit()
    
    assert user.last_login is not None
    assert isinstance(user.last_login, datetime)

def test_user_account_lockout(db_session):
    """Test account lockout functionality."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpass',
        full_name='Test User',
        role='member'
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.is_active is True
    
    # Simulate failed login attempts
    for _ in range(5):
        user.increment_failed_login_attempts()
    
    assert user.is_active is False
    assert user.failed_login_attempts == 5

def test_user_reset_password(db_session):
    """Test password reset functionality."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='oldpass',
        full_name='Test User',
        role='member'
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.verify_password('oldpass') is True
    
    user.set_password('newpass')
    db_session.commit()
    
    assert user.verify_password('newpass') is True
    assert user.verify_password('oldpass') is False

def test_user_preferences(db_session):
    """Test user preferences."""
    user = User(
        username='testuser',
        email='test@example.com',
        password='testpass',
        full_name='Test User',
        role='member'
    )
    db_session.add(user)
    db_session.commit()
    
    user.preferences = {
        'theme': 'dark',
        'notifications': True,
        'language': 'en'
    }
    db_session.commit()
    
    assert user.preferences['theme'] == 'dark'
    assert user.preferences['notifications'] is True
    assert user.preferences['language'] == 'en' 