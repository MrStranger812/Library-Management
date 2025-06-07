import pytest
from flask import url_for
from models.user import User
from models.book import Book
from models.borrowing import Borrowing
from models.fine import Fine
from tests.fixtures.test_data import create_test_user, create_test_book
from datetime import datetime, timedelta

def test_home_page(client):
    """Test the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Library Management System' in response.data

def test_user_registration(client, db_session):
    """Test user registration process."""
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'Test123!',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'

def test_user_login_logout(client, db_session):
    """Test user login and logout functionality."""
    # Create test user
    user = create_test_user(db_session)
    
    # Test login
    response = client.post('/auth/login', data={
        'username': user.username,
        'password': 'Test123!'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome' in response.data
    
    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_book_borrowing_flow(client, db_session):
    """Test the complete book borrowing process."""
    # Create test user and book
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Login
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Test123!'
    })
    
    # Borrow book
    response = client.post(f'/api/borrowings/borrow', json={
        'book_id': book.book_id,
        'days': 14
    })
    assert response.status_code == 200
    
    borrowing = Borrowing.query.filter_by(
        user_id=user.user_id,
        book_id=book.book_id
    ).first()
    assert borrowing is not None
    assert borrowing.status == 'borrowed'
    
    # Check user's borrowings
    response = client.get('/api/borrowings/user')
    assert response.status_code == 200
    assert str(book.book_id).encode() in response.data
    
    # Return book
    response = client.post(f'/api/borrowings/return', json={
        'borrowing_id': borrowing.borrowing_id
    })
    assert response.status_code == 200
    
    borrowing = Borrowing.query.get(borrowing.borrowing_id)
    assert borrowing.status == 'returned'

def test_fine_management(client, db_session):
    """Test fine creation and payment process."""
    # Create test user and book
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Create overdue borrowing
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow() - timedelta(days=30),
        due_date=datetime.utcnow() - timedelta(days=15),
        return_date=datetime.utcnow(),
        status='returned'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    # Login as admin
    admin = create_test_user(db_session, role='admin')
    client.post('/auth/login', data={
        'username': admin.username,
        'password': 'Test123!'
    })
    
    # Create fine
    response = client.post('/api/fines', json={
        'user_id': user.user_id,
        'borrowing_id': borrowing.borrowing_id,
        'amount': 15.00,
        'reason': 'overdue'
    })
    assert response.status_code == 200
    
    fine = Fine.query.filter_by(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id
    ).first()
    assert fine is not None
    assert fine.amount == 15.00
    
    # Pay fine
    response = client.post(f'/api/fines/{fine.fine_id}/pay', json={
        'amount': 15.00
    })
    assert response.status_code == 200
    
    fine = Fine.query.get(fine.fine_id)
    assert fine.status == 'paid'

def test_admin_functions(client, db_session):
    """Test administrative functions."""
    # Create admin user
    admin = create_test_user(db_session, role='admin')
    
    # Login as admin
    client.post('/auth/login', data={
        'username': admin.username,
        'password': 'Test123!'
    })
    
    # Test user management
    response = client.get('/api/users')
    assert response.status_code == 200
    
    # Test book management
    response = client.post('/api/books', json={
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '1234567890',
        'publication_year': 2024,
        'total_copies': 5
    })
    assert response.status_code == 200
    
    # Test fine management
    response = client.get('/api/fines')
    assert response.status_code == 200

def test_search_functionality(client, db_session):
    """Test search functionality."""
    # Create test books
    book1 = create_test_book(db_session, title='Python Programming')
    book2 = create_test_book(db_session, title='Java Programming')
    
    # Test search
    response = client.get('/api/books/search?q=Python')
    assert response.status_code == 200
    assert b'Python Programming' in response.data
    assert b'Java Programming' not in response.data

def test_user_profile(client, db_session):
    """Test user profile management."""
    # Create test user
    user = create_test_user(db_session)
    
    # Login
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Test123!'
    })
    
    # Update profile
    response = client.put('/api/users/profile', json={
        'full_name': 'Updated Name',
        'email': 'updated@example.com'
    })
    assert response.status_code == 200
    
    # Verify changes
    user = User.query.get(user.user_id)
    assert user.full_name == 'Updated Name'
    assert user.email == 'updated@example.com'

def test_invalid_registration(client, db_session):
    """Test registration validation and error handling."""
    # Test missing required fields
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'Test123!'
    }, follow_redirects=True)
    assert response.status_code == 400
    assert b'Email is required' in response.data
    
    # Test invalid email format
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'Test123!',
        'email': 'invalid-email',
        'full_name': 'Test User'
    }, follow_redirects=True)
    assert response.status_code == 400
    assert b'Invalid email format' in response.data
    
    # Test weak password
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'weak',
        'email': 'test@example.com',
        'full_name': 'Test User'
    }, follow_redirects=True)
    assert response.status_code == 400
    assert b'Password too weak' in response.data
    
    # Test duplicate username
    user = create_test_user(db_session)
    response = client.post('/auth/register', data={
        'username': user.username,
        'password': 'Test123!',
        'email': 'test2@example.com',
        'full_name': 'Test User'
    }, follow_redirects=True)
    assert response.status_code == 400
    assert b'Username already exists' in response.data

def test_invalid_login(client, db_session):
    """Test login validation and error handling."""
    user = create_test_user(db_session)
    
    # Test invalid credentials
    response = client.post('/auth/login', data={
        'username': user.username,
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 401
    assert b'Invalid username or password' in response.data
    
    # Test account lockout
    for _ in range(5):  # Assuming 5 failed attempts triggers lockout
        client.post('/auth/login', data={
            'username': user.username,
            'password': 'wrongpassword'
        })
    
    response = client.post('/auth/login', data={
        'username': user.username,
        'password': 'Test123!'
    }, follow_redirects=True)
    assert response.status_code == 403
    assert b'Account locked' in response.data

def test_unauthorized_access(client, db_session):
    """Test unauthorized access to protected routes."""
    # Test accessing admin routes without admin role
    user = create_test_user(db_session)
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Test123!'
    })
    
    response = client.get('/api/users')
    assert response.status_code == 403
    assert b'Permission denied' in response.data
    
    response = client.post('/api/books', json={
        'title': 'Test Book',
        'author': 'Test Author',
        'isbn': '1234567890',
        'publication_year': 2024,
        'total_copies': 5
    })
    assert response.status_code == 403
    assert b'Permission denied' in response.data

def test_book_borrowing_validation(client, db_session):
    """Test book borrowing validation and error handling."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Login
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Test123!'
    })
    
    # Test borrowing with invalid book ID
    response = client.post('/api/borrowings/borrow', json={
        'book_id': 99999,
        'days': 14
    })
    assert response.status_code == 404
    assert b'Book not found' in response.data
    
    # Test borrowing with invalid days
    response = client.post('/api/borrowings/borrow', json={
        'book_id': book.book_id,
        'days': 0
    })
    assert response.status_code == 400
    assert b'Invalid borrowing period' in response.data
    
    # Test borrowing with no available copies
    book.total_copies = 0
    db_session.commit()
    
    response = client.post('/api/borrowings/borrow', json={
        'book_id': book.book_id,
        'days': 14
    })
    assert response.status_code == 400
    assert b'No copies available' in response.data

def test_fine_management_validation(client, db_session):
    """Test fine management validation and error handling."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    admin = create_test_user(db_session, role='admin')
    
    # Create overdue borrowing
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow() - timedelta(days=30),
        due_date=datetime.utcnow() - timedelta(days=15),
        return_date=datetime.utcnow(),
        status='returned'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    # Login as admin
    client.post('/auth/login', data={
        'username': admin.username,
        'password': 'Test123!'
    })
    
    # Test creating fine with invalid amount
    response = client.post('/api/fines', json={
        'user_id': user.user_id,
        'borrowing_id': borrowing.borrowing_id,
        'amount': -10.00,
        'reason': 'overdue'
    })
    assert response.status_code == 400
    assert b'Invalid fine amount' in response.data
    
    # Test creating fine with invalid reason
    response = client.post('/api/fines', json={
        'user_id': user.user_id,
        'borrowing_id': borrowing.borrowing_id,
        'amount': 15.00,
        'reason': 'invalid_reason'
    })
    assert response.status_code == 400
    assert b'Invalid fine reason' in response.data
    
    # Create valid fine
    fine = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=15.00,
        reason='overdue',
        status='pending'
    )
    db_session.add(fine)
    db_session.commit()
    
    # Test paying fine with invalid amount
    response = client.post(f'/api/fines/{fine.fine_id}/pay', json={
        'amount': 20.00  # More than fine amount
    })
    assert response.status_code == 400
    assert b'Invalid payment amount' in response.data

def test_search_validation(client, db_session):
    """Test search functionality validation and error handling."""
    # Test search with empty query
    response = client.get('/api/books/search?q=')
    assert response.status_code == 400
    assert b'Search query required' in response.data
    
    # Test search with invalid parameters
    response = client.get('/api/books/search?q=test&page=0')
    assert response.status_code == 400
    assert b'Invalid page number' in response.data
    
    response = client.get('/api/books/search?q=test&per_page=0')
    assert response.status_code == 400
    assert b'Invalid items per page' in response.data

def test_user_profile_validation(client, db_session):
    """Test user profile management validation and error handling."""
    user = create_test_user(db_session)
    
    # Login
    client.post('/auth/login', data={
        'username': user.username,
        'password': 'Test123!'
    })
    
    # Test updating profile with invalid email
    response = client.put('/api/users/profile', json={
        'full_name': 'Updated Name',
        'email': 'invalid-email'
    })
    assert response.status_code == 400
    assert b'Invalid email format' in response.data
    
    # Test updating profile with empty name
    response = client.put('/api/users/profile', json={
        'full_name': '',
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    assert b'Full name required' in response.data 