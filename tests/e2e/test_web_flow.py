import pytest
from flask import url_for
from tests.fixtures.test_data import create_test_user, create_test_book
from datetime import datetime, timedelta

def test_home_page(client):
    """Test the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Library Management System' in response.data

def test_user_registration(client, db_session):
    """Test user registration flow."""
    # Test registration page
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    
    # Test registration submission
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    # Verify user was created
    user = db_session.query(User).filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'

def test_user_login_logout(client, db_session):
    """Test user login and logout flow."""
    # Create test user
    user = create_test_user(db_session)
    
    # Test login page
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    
    # Test login with correct credentials
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Welcome' in response.data
    
    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_book_borrowing_flow(client, db_session):
    """Test the complete book borrowing flow through the web interface."""
    # Create test data
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    book.add_copies(2)
    db_session.commit()
    
    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Browse books
    response = client.get('/books')
    assert response.status_code == 200
    assert book.title.encode() in response.data
    
    # View book details
    response = client.get(f'/books/{book.id}')
    assert response.status_code == 200
    assert book.title.encode() in response.data
    assert b'Borrow' in response.data
    
    # Borrow book
    response = client.post(f'/books/{book.id}/borrow', follow_redirects=True)
    assert response.status_code == 200
    assert b'Book borrowed successfully' in response.data
    
    # Check my borrowings
    response = client.get('/my-borrowings')
    assert response.status_code == 200
    assert book.title.encode() in response.data
    
    # Return book
    response = client.post(f'/books/{book.id}/return', follow_redirects=True)
    assert response.status_code == 200
    assert b'Book returned successfully' in response.data

def test_fine_management_flow(client, db_session):
    """Test the fine management flow through the web interface."""
    # Create test data
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    book.add_copies(1)
    
    # Create overdue borrowing
    borrowing = user.borrow_book(book)
    borrowing.borrow_date = datetime.utcnow() - timedelta(days=30)
    borrowing.due_date = datetime.utcnow() - timedelta(days=15)
    db_session.commit()
    
    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Check fines
    response = client.get('/my-fines')
    assert response.status_code == 200
    assert b'15.00' in response.data  # Fine amount
    
    # Pay fine
    response = client.post(f'/fines/{borrowing.fine.id}/pay', follow_redirects=True)
    assert response.status_code == 200
    assert b'Fine paid successfully' in response.data
    
    # Verify fine status
    response = client.get('/my-fines')
    assert response.status_code == 200
    assert b'Paid' in response.data

def test_admin_flow(client, db_session):
    """Test the admin management flow through the web interface."""
    # Create admin user
    admin = create_test_user(db_session, role='admin')
    
    # Login as admin
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Access admin dashboard
    response = client.get('/admin')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data
    
    # Add new book
    response = client.post('/admin/books/add', data={
        'title': 'New Book',
        'author': 'New Author',
        'isbn': '1234567890',
        'publisher': 'New Publisher',
        'publication_year': '2023',
        'total_copies': '5'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Book added successfully' in response.data
    
    # Verify book was added
    response = client.get('/admin/books')
    assert response.status_code == 200
    assert b'New Book' in response.data

def test_search_functionality(client, db_session):
    """Test the search functionality through the web interface."""
    # Create test books
    book1 = create_test_book(db_session)
    book1.title = 'Python Programming'
    book2 = create_test_book(db_session)
    book2.title = 'Java Programming'
    db_session.commit()
    
    # Test search by title
    response = client.get('/search?q=Python')
    assert response.status_code == 200
    assert b'Python Programming' in response.data
    assert b'Java Programming' not in response.data
    
    # Test search by author
    response = client.get('/search?q=Author')
    assert response.status_code == 200
    assert b'Python Programming' in response.data
    assert b'Java Programming' in response.data

def test_user_profile_management(client, db_session):
    """Test user profile management through the web interface."""
    # Create test user
    user = create_test_user(db_session)
    
    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # View profile
    response = client.get('/profile')
    assert response.status_code == 200
    assert b'testuser' in response.data
    
    # Update profile
    response = client.post('/profile', data={
        'email': 'updated@example.com',
        'current_password': 'testpass',
        'new_password': 'newpass123',
        'confirm_password': 'newpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Profile updated successfully' in response.data
    
    # Verify changes
    updated_user = db_session.query(User).get(user.id)
    assert updated_user.email == 'updated@example.com'
    assert updated_user.check_password('newpass123') 