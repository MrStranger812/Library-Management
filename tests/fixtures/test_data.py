from datetime import datetime, timedelta
from models.user import User
from models.book import Book, BookCopy
from models.borrowing import Borrowing
from models.fine import Fine
from models.tag import Tag
from werkzeug.security import generate_password_hash

def create_test_user(db_session, role='member'):
    """Create a test user."""
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('testpass'),
        role=role,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user

def create_test_book(db_session):
    """Create a test book."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='1234567890',
        publisher='Test Publisher',
        publication_year=2023,
        description='Test Description',
        total_copies=5,
        available_copies=5
    )
    db_session.add(book)
    db_session.commit()
    return book

def create_test_borrowing(db_session, user, book):
    """Create a test borrowing record."""
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        return_date=None,
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    return borrowing

def create_test_fine(db_session, borrowing):
    """Create a test fine."""
    fine = Fine(
        borrowing_id=borrowing.id,
        amount=10.00,
        status='unpaid',
        created_at=datetime.utcnow()
    )
    db_session.add(fine)
    db_session.commit()
    return fine

def create_test_tag(db_session):
    """Create a test tag."""
    tag = Tag(
        name='Test Tag',
        color='#FF0000',
        description='Test Tag Description'
    )
    db_session.add(tag)
    db_session.commit()
    return tag 