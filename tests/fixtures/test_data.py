# tests/fixtures/test_data.py
from datetime import datetime, timedelta
from models.user import User
from models.book import Book, Publisher, Category
from models.borrowing import Borrowing
from models.fine import Fine
from models.tag import Tag

def create_test_user(db_session, username='testuser', role='member'):
    """Create a test user with proper initialization."""
    user = User(
        username=username,
        email=f'{username}@example.com',
        full_name=f'Test {username.title()}',
        role=role
    )
    user.set_password('Test123!')  # Use a password that meets security requirements
    db_session.add(user)
    db_session.commit()
    return user

def create_test_book(db_session, title='Test Book', isbn=None):
    """Create a test book with all required fields."""
    # First create publisher and category if they don't exist
    publisher = Publisher.query.filter_by(name='Test Publisher').first()
    if not publisher:
        publisher = Publisher(
            name='Test Publisher',
            address='123 Test St',
            email='publisher@test.com'
        )
        db_session.add(publisher)
        db_session.commit()
    
    category = Category.query.filter_by(name='Test Category').first()
    if not category:
        category = Category(
            name='Test Category',
            description='Category for testing'
        )
        db_session.add(category)
        db_session.commit()
    
    # Generate unique ISBN if not provided
    if not isbn:
        import uuid
        isbn = str(uuid.uuid4())[:13]
    
    book = Book(
        isbn=isbn,
        title=title,
        author='Test Author',  # This is still required based on schema
        publisher_id=publisher.publisher_id,
        category_id=category.category_id,
        publication_year=2023,
        description='Test Description',
        total_copies=5,
        copies_available=5
    )
    db_session.add(book)
    db_session.commit()
    return book

def create_test_borrowing(db_session, user, book, days_ago=0, duration=14):
    """Create a test borrowing record."""
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        due_date=datetime.now().date() + timedelta(days=duration-days_ago)
    )
    if days_ago > 0:
        borrowing.borrow_date = datetime.now().date() - timedelta(days=days_ago)
    db_session.add(borrowing)
    db_session.commit()
    
    # Update book availability
    book.copies_available -= 1
    db_session.commit()
    
    return borrowing

def create_test_fine(db_session, borrowing, amount=10.00):
    """Create a test fine."""
    fine = Fine(
        borrowing_id=borrowing.borrowing_id,
        amount=amount,
        reason='Overdue book'
    )
    db_session.add(fine)
    db_session.commit()
    return fine

def create_test_tag(db_session, name='Test Tag'):
    """Create a test tag."""
    tag = Tag(
        name=name,
        color='#FF0000',
        description='Test Tag Description'
    )
    db_session.add(tag)
    db_session.commit()
    return tag