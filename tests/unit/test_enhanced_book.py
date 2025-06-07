"""
Unit tests for the EnhancedBook model.
Tests the advanced book management functionality.
"""

import pytest
from datetime import date
from models.enhanced_book import EnhancedBook
from models.book import Book
from models.author import Author
from models.publisher import Publisher
from models.category import Category

class TestEnhancedBook:
    """Test cases for EnhancedBook model."""

    def test_create_book_success(self, db_session):
        """Test successful book creation with authors."""
        # Create test data
        publisher = Publisher(
            name="Test Publisher",
            address="Test Address",
            phone="1234567890",
            email="publisher@test.com"
        )
        category = Category(
            name="Test Category",
            description="Test Description"
        )
        authors = [
            Author(
                name="Author One",
                biography="Test Biography 1"
            ),
            Author(
                name="Author Two",
                biography="Test Biography 2"
            )
        ]
        
        db_session.add_all([publisher, category] + authors)
        db_session.commit()
        
        # Create book
        success, result = EnhancedBook.create(
            isbn="1234567890",
            title="Test Book",
            publisher_id=publisher.publisher_id,
            category_id=category.category_id,
            publication_year=2024,
            total_copies=5,
            author_ids=[author.author_id for author in authors]
        )
        
        assert success is True
        assert "created successfully" in result
        
        # Verify book creation
        book = Book.query.filter_by(isbn="1234567890").first()
        assert book is not None
        assert book.title == "Test Book"
        assert book.publisher_id == publisher.publisher_id
        assert book.category_id == category.category_id
        assert book.publication_year == 2024
        assert book.total_copies == 5
        assert book.copies_available == 5
        
        # Verify author associations
        assert len(book.authors) == 2
        author_names = {author.name for author in book.authors}
        assert author_names == {"Author One", "Author Two"}

    def test_create_book_missing_required_fields(self, db_session):
        """Test book creation with missing required fields."""
        # Attempt to create book without ISBN and title
        success, result = EnhancedBook.create(
            isbn="",
            title="",
            publisher_id=1,
            category_id=1,
            publication_year=2024,
            total_copies=5
        )
        
        assert success is False
        assert "ISBN and title are required" in result

    def test_get_with_details(self, db_session):
        """Test retrieving book details with related information."""
        # Create test data
        publisher = Publisher(
            name="Test Publisher",
            address="Test Address",
            phone="1234567890",
            email="publisher@test.com"
        )
        category = Category(
            name="Test Category",
            description="Test Description"
        )
        author = Author(
            name="Test Author",
            biography="Test Biography"
        )
        book = Book(
            isbn="1234567890",
            title="Test Book",
            publisher_id=publisher.publisher_id,
            category_id=category.category_id,
            publication_year=2024,
            total_copies=5,
            copies_available=5
        )
        
        db_session.add_all([publisher, category, author, book])
        db_session.commit()
        
        # Associate author with book
        book.authors.append(author)
        db_session.commit()
        
        # Get book details
        details = EnhancedBook.get_with_details(book.book_id)
        
        assert details is not None
        assert details['isbn'] == "1234567890"
        assert details['title'] == "Test Book"
        assert details['publisher_name'] == "Test Publisher"
        assert details['category_name'] == "Test Category"
        assert details['publication_year'] == 2024
        assert details['total_copies'] == 5
        assert details['copies_available'] == 5
        assert len(details['authors']) == 1
        assert details['authors'][0]['name'] == "Test Author"

    def test_search_advanced(self, db_session):
        """Test advanced book search functionality."""
        # Create test data
        publisher = Publisher(
            name="Test Publisher",
            address="Test Address",
            phone="1234567890",
            email="publisher@test.com"
        )
        category = Category(
            name="Test Category",
            description="Test Description"
        )
        author = Author(
            name="Test Author",
            biography="Test Biography"
        )
        books = [
            Book(
                isbn="1234567890",
                title="Python Programming",
                publisher_id=publisher.publisher_id,
                category_id=category.category_id,
                publication_year=2024,
                total_copies=5,
                copies_available=5
            ),
            Book(
                isbn="0987654321",
                title="Java Programming",
                publisher_id=publisher.publisher_id,
                category_id=category.category_id,
                publication_year=2023,
                total_copies=3,
                copies_available=0
            )
        ]
        
        db_session.add_all([publisher, category, author] + books)
        db_session.commit()
        
        # Associate author with books
        for book in books:
            book.authors.append(author)
        db_session.commit()
        
        # Test search by title
        results = EnhancedBook.search_advanced(title="Python")
        assert len(results) == 1
        assert results[0]['title'] == "Python Programming"
        
        # Test search by author
        results = EnhancedBook.search_advanced(author="Test Author")
        assert len(results) == 2
        
        # Test search by availability
        results = EnhancedBook.search_advanced(available_only=True)
        assert len(results) == 1
        assert results[0]['title'] == "Python Programming"
        
        # Test search by publication year range
        results = EnhancedBook.search_advanced(
            year_start=2023,
            year_end=2024
        )
        assert len(results) == 2 