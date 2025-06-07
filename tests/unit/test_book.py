import pytest
from models.book import Book, BookCopy
from models.tag import Tag
from datetime import datetime

def test_create_book(db_session):
    """Test book creation."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='1234567890',
        publisher='Test Publisher',
        publication_year=2023,
        description='Test Description',
        total_copies=5,
        copies_available=5
    )
    db_session.add(book)
    db_session.commit()
    
    assert book.book_id is not None
    assert book.title == 'Test Book'
    assert book.author == 'Test Author'
    assert book.isbn == '1234567890'
    assert book.total_copies == 5
    assert book.copies_available == 5

def test_book_isbn_validation(db_session):
    """Test ISBN validation."""
    with pytest.raises(ValueError):
        Book(
            title='Test Book',
            author='Test Author',
            isbn='invalid_isbn',
            publisher='Test Publisher',
            publication_year=2023
        )

def test_book_publication_year_validation(db_session):
    """Test publication year validation."""
    with pytest.raises(ValueError):
        Book(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            publisher='Test Publisher',
            publication_year=datetime.now().year + 1
        )

def test_book_copy_management(db_session):
    """Test book copy management."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='1234567890',
        publisher='Test Publisher',
        publication_year=2023
    )
    db_session.add(book)
    db_session.commit()
    
    # Add copies
    book.add_copies(3)
    db_session.commit()
    
    assert book.total_copies == 3
    assert book.copies_available == 3
    
    # Remove copies
    book.remove_copies(1)
    db_session.commit()
    
    assert book.total_copies == 2
    assert book.copies_available == 2

def test_book_availability(db_session):
    """Test book availability tracking."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='1234567890',
        publisher='Test Publisher',
        publication_year=2023
    )
    db_session.add(book)
    book.add_copies(2)
    db_session.commit()
    
    assert book.is_available() is True
    
    # Borrow a copy
    book.borrow_copy()
    db_session.commit()
    
    assert book.copies_available == 1
    assert book.is_available() is True
    
    # Borrow another copy
    book.borrow_copy()
    db_session.commit()
    
    assert book.copies_available == 0
    assert book.is_available() is False

def test_book_tags(db_session):
    """Test book tagging system."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='1234567890',
        publisher='Test Publisher',
        publication_year=2023
    )
    db_session.add(book)
    
    tag1 = Tag(name='Fiction', color='#FF0000')
    tag2 = Tag(name='Mystery', color='#00FF00')
    db_session.add_all([tag1, tag2])
    db_session.commit()
    
    book.add_tag(tag1)
    book.add_tag(tag2)
    db_session.commit()
    
    assert len(book.tags) == 2
    assert tag1 in book.tags
    assert tag2 in book.tags
    
    book.remove_tag(tag1)
    db_session.commit()
    
    assert len(book.tags) == 1
    assert tag1 not in book.tags
    assert tag2 in book.tags

def test_book_search(db_session):
    """Test book search functionality."""
    book1 = Book(
        title='Python Programming',
        author='John Doe',
        isbn='1234567890',
        publisher='Tech Books',
        publication_year=2023
    )
    book2 = Book(
        title='Java Programming',
        author='Jane Smith',
        isbn='0987654321',
        publisher='Code Books',
        publication_year=2023
    )
    db_session.add_all([book1, book2])
    db_session.commit()
    
    # Test title search
    results = Book.search('Python')
    assert len(results) == 1
    assert results[0].title == 'Python Programming'
    
    # Test author search
    results = Book.search('Smith')
    assert len(results) == 1
    assert results[0].author == 'Jane Smith'

def test_book_copy_status(db_session):
    """Test book copy status tracking."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='1234567890',
        publisher='Test Publisher',
        publication_year=2023
    )
    db_session.add(book)
    book.add_copies(1)
    db_session.commit()
    
    copy = book.copies[0]
    assert copy.status == 'available'
    
    copy.status = 'borrowed'
    db_session.commit()
    
    assert copy.status == 'borrowed'
    assert book.copies_available == 0

def test_book_statistics(db_session):
    """Test book statistics tracking."""
    book = Book(
        title='Test Book',
        author='Test Author',
        isbn='1234567890',
        publisher='Test Publisher',
        publication_year=2023
    )
    db_session.add(book)
    book.add_copies(3)
    db_session.commit()
    
    # Simulate some borrowing activity
    book.borrow_copy()
    book.borrow_copy()
    db_session.commit()
    
    assert book.total_copies == 3
    assert book.copies_available == 1
    assert book.borrowed_copies == 2 