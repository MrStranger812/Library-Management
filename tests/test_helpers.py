import uuid
from datetime import datetime, timedelta
from models.user import User
from models.book import Book, Publisher, Category
from models.borrowing import Borrowing
from models.fine import Fine
from test_config import TestConfig

def create_test_user(db_session, role='member', **kwargs):
    """Create a test user with default or custom attributes."""
    username = kwargs.get('username', f'testuser_{uuid.uuid4().hex[:8]}')
    user = User(
        username=username,
        email=kwargs.get('email', f'{username}@example.com'),
        full_name=kwargs.get('full_name', 'Test User'),
        role=role
    )
    user.set_password(kwargs.get('password', TestConfig.TEST_USER_PASSWORD))
    db_session.add(user)
    db_session.commit()
    return user

def create_test_book(db_session, **kwargs):
    """Create a test book with default or custom attributes."""
    # Create required related objects if not provided
    if 'publisher_id' not in kwargs:
        publisher = Publisher(
            name=f'Test Publisher {uuid.uuid4().hex[:4]}',
            email=f'publisher_{uuid.uuid4().hex[:4]}@example.com'
        )
        db_session.add(publisher)
        db_session.commit()
        kwargs['publisher_id'] = publisher.publisher_id
    
    if 'category_id' not in kwargs:
        category = Category(
            name=f'Test Category {uuid.uuid4().hex[:4]}',
            description='Test category description'
        )
        db_session.add(category)
        db_session.commit()
        kwargs['category_id'] = category.category_id
    
    # Create book with defaults or custom values
    book = Book(
        isbn=kwargs.get('isbn', str(uuid.uuid4().int)[:13]),
        title=kwargs.get('title', f'Test Book {uuid.uuid4().hex[:4]}'),
        author=kwargs.get('author', 'Test Author'),
        publisher_id=kwargs['publisher_id'],
        category_id=kwargs['category_id'],
        publication_year=kwargs.get('publication_year', datetime.now().year),
        total_copies=kwargs.get('total_copies', 5),
        copies_available=kwargs.get('copies_available', 5)
    )
    db_session.add(book)
    db_session.commit()
    return book

def create_test_borrowing(db_session, user_id, book_id, **kwargs):
    """Create a test borrowing record."""
    borrowing = Borrowing(
        user_id=user_id,
        book_id=book_id,
        borrow_date=kwargs.get('borrow_date', datetime.now()),
        due_date=kwargs.get('due_date', datetime.now() + timedelta(days=14)),
        return_date=kwargs.get('return_date'),
        status=kwargs.get('status', 'borrowed')
    )
    db_session.add(borrowing)
    db_session.commit()
    return borrowing

def create_test_fine(db_session, borrowing_id, **kwargs):
    """Create a test fine record."""
    fine = Fine(
        borrowing_id=borrowing_id,
        amount=kwargs.get('amount', 10.00),
        status=kwargs.get('status', 'pending'),
        due_date=kwargs.get('due_date', datetime.now() + timedelta(days=7))
    )
    db_session.add(fine)
    db_session.commit()
    return fine

def generate_unique_isbn():
    """Generate a unique ISBN for testing."""
    return str(uuid.uuid4().int)[:13]

def generate_unique_email():
    """Generate a unique email for testing."""
    return f'test_{uuid.uuid4().hex[:8]}@example.com' 