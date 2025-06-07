"""
Unit tests for the EnhancedBorrowing model.
Tests the advanced borrowing management functionality.
"""

import pytest
from datetime import date, timedelta
from models.enhanced_borrowing import EnhancedBorrowing
from models.user import User
from models.book import Book
from models.book_copy import BookCopy
from models.membership_type import MembershipType
from models.user_membership import UserMembership
from models.borrowing import Borrowing

class TestEnhancedBorrowing:
    """Test cases for EnhancedBorrowing model."""

    def test_borrow_book_copy_success(self, db_session):
        """Test successful book borrowing."""
        # Create test data
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        membership_type = MembershipType(
            name="Standard",
            max_books_allowed=5,
            loan_duration_days=14
        )
        user_membership = UserMembership(
            user_id=user.user_id,
            membership_type_id=membership_type.membership_type_id,
            is_active=True,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365)
        )
        book = Book(
            isbn="1234567890",
            title="Test Book",
            total_copies=5,
            copies_available=5
        )
        book_copy = BookCopy(
            book_id=book.book_id,
            is_available=True,
            barcode="TEST123"
        )
        
        db_session.add_all([user, membership_type, user_membership, book, book_copy])
        db_session.commit()
        
        # Borrow book
        success, result = EnhancedBorrowing.borrow_book_copy(
            user_id=user.user_id,
            copy_id=book_copy.copy_id
        )
        
        assert success is True
        assert "borrowed successfully" in result
        
        # Verify borrowing record
        borrowing = Borrowing.query.filter_by(
            user_id=user.user_id,
            copy_id=book_copy.copy_id
        ).first()
        assert borrowing is not None
        assert borrowing.status == "borrowed"
        assert borrowing.due_date == date.today() + timedelta(days=14)
        
        # Verify book copy availability
        book_copy = BookCopy.query.get(book_copy.copy_id)
        assert book_copy.is_available is False
        
        # Verify book availability count
        book = Book.query.get(book.book_id)
        assert book.copies_available == 4

    def test_borrow_book_copy_no_membership(self, db_session):
        """Test book borrowing without active membership."""
        # Create test data
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        book = Book(
            isbn="1234567890",
            title="Test Book",
            total_copies=5,
            copies_available=5
        )
        book_copy = BookCopy(
            book_id=book.book_id,
            is_available=True,
            barcode="TEST123"
        )
        
        db_session.add_all([user, book, book_copy])
        db_session.commit()
        
        # Attempt to borrow book
        success, result = EnhancedBorrowing.borrow_book_copy(
            user_id=user.user_id,
            copy_id=book_copy.copy_id
        )
        
        assert success is False
        assert "No valid membership found" in result

    def test_borrow_book_copy_max_limit_reached(self, db_session):
        """Test book borrowing when maximum limit is reached."""
        # Create test data
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        membership_type = MembershipType(
            name="Standard",
            max_books_allowed=2,
            loan_duration_days=14
        )
        user_membership = UserMembership(
            user_id=user.user_id,
            membership_type_id=membership_type.membership_type_id,
            is_active=True,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365)
        )
        
        # Create books and copies
        books = []
        copies = []
        for i in range(3):
            book = Book(
                isbn=f"123456789{i}",
                title=f"Test Book {i}",
                total_copies=5,
                copies_available=5
            )
            copy = BookCopy(
                book_id=book.book_id,
                is_available=True,
                barcode=f"TEST{i}"
            )
            books.append(book)
            copies.append(copy)
        
        db_session.add_all([user, membership_type, user_membership] + books + copies)
        db_session.commit()
        
        # Borrow first two books
        for i in range(2):
            success, result = EnhancedBorrowing.borrow_book_copy(
                user_id=user.user_id,
                copy_id=copies[i].copy_id
            )
            assert success is True
        
        # Attempt to borrow third book
        success, result = EnhancedBorrowing.borrow_book_copy(
            user_id=user.user_id,
            copy_id=copies[2].copy_id
        )
        
        assert success is False
        assert "Maximum borrowing limit" in result

    def test_get_user_borrowings_detailed(self, db_session):
        """Test retrieving detailed borrowing information."""
        # Create test data
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User"
        )
        membership_type = MembershipType(
            name="Standard",
            max_books_allowed=5,
            loan_duration_days=14
        )
        user_membership = UserMembership(
            user_id=user.user_id,
            membership_type_id=membership_type.membership_type_id,
            is_active=True,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365)
        )
        book = Book(
            isbn="1234567890",
            title="Test Book",
            total_copies=5,
            copies_available=5
        )
        book_copy = BookCopy(
            book_id=book.book_id,
            is_available=True,
            barcode="TEST123"
        )
        
        db_session.add_all([user, membership_type, user_membership, book, book_copy])
        db_session.commit()
        
        # Create borrowing
        borrowing = Borrowing(
            user_id=user.user_id,
            book_id=book.book_id,
            copy_id=book_copy.copy_id,
            borrow_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            status="borrowed"
        )
        db_session.add(borrowing)
        db_session.commit()
        
        # Get borrowing details
        details = EnhancedBorrowing.get_user_borrowings_detailed(user.user_id)
        
        assert len(details) == 1
        assert details[0]['title'] == "Test Book"
        assert details[0]['status'] == "borrowed"
        assert details[0]['barcode'] == "TEST123"
        assert details[0]['days_overdue'] == 0 