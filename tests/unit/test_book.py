import pytest
from models.book import Book, Publisher, Category
from models.tag import Tag, BookTag
from datetime import datetime

def test_create_book(db_session):
    """Test book creation."""
    # Create publisher and category first
    publisher = Publisher(name='Test Publisher')
    category = Category(name='Test Category')
    db_session.add_all([publisher, category])
    db_session.commit()
    
    book = Book(
        isbn='1234567890',
        title='Test Book',
        author='Test Author',
        publisher_id=publisher.publisher_id,
        category_id=category.category_id,
        publication_year=2023,
        description='Test Description',
        total_copies=5
    )
    db_session.add(book)
    db_session.commit()
    
    assert book.book_id is not None
    assert book.title == 'Test Book'
    assert book.author == 'Test Author'
    assert book.isbn == '1234567890'
    assert book.total_copies == 5
    assert book.copies_available == 5  # Should match total_copies initially

def test_book_unique_isbn(db_session):
    """Test ISBN uniqueness constraint."""
    book1 = Book(
        isbn='1234567890',
        title='Book 1',
        author='Author 1',
        total_copies=1
    )
    db_session.add(book1)
    db_session.commit()
    
    # Try to create another book with same ISBN
    book2 = Book(
        isbn='1234567890',
        title='Book 2',
        author='Author 2',
        total_copies=1
    )
    db_session.add(book2)
    
    with pytest.raises(Exception):  # Should raise IntegrityError
        db_session.commit()

def test_book_copy_management(db_session):
    """Test book copy availability tracking."""
    book = Book(
        isbn='1234567890',
        title='Test Book',
        author='Test Author',
        total_copies=3
    )
    db_session.add(book)
    db_session.commit()
    
    assert book.total_copies == 3
    assert book.copies_available == 3
    
    # Manually update available copies (simulating borrowing)
    book.copies_available -= 1
    db_session.commit()
    
    assert book.copies_available == 2
    assert book.total_copies == 3  # Total should remain unchanged

def test_book_tags(db_session):
    """Test book tagging system."""
    book = Book(
        isbn='1234567890',
        title='Test Book',
        author='Test Author',
        total_copies=1
    )
    db_session.add(book)
    
    tag1 = Tag(name='Fiction', color='#FF0000')
    tag2 = Tag(name='Mystery', color='#00FF00')
    db_session.add_all([tag1, tag2])
    db_session.commit()
    
    # Add tags to book using the association table
    book_tag1 = BookTag(book_id=book.book_id, tag_id=tag1.tag_id)
    book_tag2 = BookTag(book_id=book.book_id, tag_id=tag2.tag_id)
    db_session.add_all([book_tag1, book_tag2])
    db_session.commit()
    
    # Query tags through relationship
    book_tags = BookTag.query.filter_by(book_id=book.book_id).all()
    assert len(book_tags) == 2
    
    tag_names = [bt.tag.name for bt in book_tags if bt.tag]
    assert 'Fiction' in tag_names
    assert 'Mystery' in tag_names

def test_book_search(db_session):
    """Test book search functionality."""
    book1 = Book(
        isbn='1234567890',
        title='Python Programming',
        author='John Doe',
        total_copies=1
    )
    book2 = Book(
        isbn='0987654321',
        title='Java Programming',
        author='Jane Smith',
        total_copies=1
    )
    db_session.add_all([book1, book2])
    db_session.commit()
    
    # Test search by title
    results = Book.search('Python')
    assert len(results) == 1
    assert results[0].title == 'Python Programming'
    
    # Test search by author
    results = Book.search('Smith')
    assert len(results) == 1
    assert results[0].author == 'Jane Smith'
    
    # Test search by ISBN
    results = Book.search('123456')
    assert len(results) == 1
    assert results[0].isbn == '1234567890'

def test_book_availability_check(db_session):
    """Test checking book availability."""
    book = Book(
        isbn='1234567890',
        title='Test Book',
        author='Test Author',
        total_copies=2
    )
    db_session.add(book)
    db_session.commit()
    
    assert book.copies_available > 0  # Book is available
    
    # Make all copies unavailable
    book.copies_available = 0
    db_session.commit()
    
    assert book.copies_available == 0  # Book is not available

def test_book_constraints(db_session):
    """Test database constraints on books table."""
    book = Book(
        isbn='1234567890',
        title='Test Book',
        author='Test Author',
        total_copies=5,
        copies_available=3
    )
    db_session.add(book)
    db_session.commit()
    
    # Test constraint: copies_available should not exceed total_copies
    book.copies_available = 6
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()
    
    # Test constraint: copies_available should not be negative
    book.copies_available = -1
    with pytest.raises(Exception):
        db_session.commit()
    db_session.rollback()