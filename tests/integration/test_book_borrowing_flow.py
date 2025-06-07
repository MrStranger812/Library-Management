import pytest
from datetime import datetime, timedelta
from models.user import User
from models.book import Book
from models.borrowing import Borrowing
from models.fine import Fine
from tests.fixtures.test_data import create_test_user, create_test_book

def test_book_borrowing_flow(db_session):
    """Test the complete book borrowing flow."""
    # Create test user and book
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Test borrowing creation
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    assert borrowing.borrowing_id is not None
    assert borrowing.status == 'borrowed'
    assert book.copies_available == book.total_copies - 1
    
    # Test overdue scenario
    borrowing.due_date = datetime.utcnow() - timedelta(days=1)
    db_session.commit()
    
    assert borrowing.is_overdue() is True
    assert borrowing.days_overdue() == 1
    
    # Test fine creation
    fine = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=1.00,  # $1 per day
        reason='overdue',
        status='pending'
    )
    db_session.add(fine)
    db_session.commit()
    
    assert fine.fine_id is not None
    assert fine.status == 'pending'
    assert user.pending_fines() == 1.00
    
    # Test book return
    borrowing.return_book()
    db_session.commit()
    
    assert borrowing.status == 'returned'
    assert borrowing.return_date is not None
    assert book.copies_available == book.total_copies
    
    # Test fine payment
    fine.pay()
    db_session.commit()
    
    assert fine.status == 'paid'
    assert fine.payment_date is not None
    assert user.pending_fines() == 0.00

def test_concurrent_borrowings(db_session):
    """Test handling of concurrent borrowings."""
    user = create_test_user(db_session)
    book1 = create_test_book(db_session)
    book2 = create_test_book(db_session)
    
    # Create first borrowing
    borrowing1 = Borrowing(
        user_id=user.user_id,
        book_id=book1.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing1)
    db_session.commit()
    
    # Create second borrowing
    borrowing2 = Borrowing(
        user_id=user.user_id,
        book_id=book2.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing2)
    db_session.commit()
    
    assert user.active_borrowings_count() == 2
    assert book1.copies_available == book1.total_copies - 1
    assert book2.copies_available == book2.total_copies - 1
    
    # Return first book
    borrowing1.return_book()
    db_session.commit()
    
    assert user.active_borrowings_count() == 1
    assert book1.copies_available == book1.total_copies
    assert book2.copies_available == book2.total_copies - 1

def test_borrowing_with_fines(db_session):
    """Test borrowing with multiple fines."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Create borrowing
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
    
    # Create multiple fines
    fine1 = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=15.00,
        reason='overdue',
        status='pending'
    )
    fine2 = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=10.00,
        reason='damage',
        status='pending'
    )
    db_session.add_all([fine1, fine2])
    db_session.commit()
    
    assert user.total_fines() == 25.00
    assert user.pending_fines() == 25.00
    
    # Pay first fine
    fine1.pay()
    db_session.commit()
    
    assert user.total_fines() == 25.00
    assert user.pending_fines() == 10.00
    
    # Pay second fine
    fine2.pay()
    db_session.commit()
    
    assert user.total_fines() == 25.00
    assert user.pending_fines() == 0.00

def test_complete_borrowing_flow(db_session):
    """Test the complete book borrowing flow."""
    # Create test data
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    book.add_copies(2)
    db_session.commit()
    
    # Step 1: Check initial state
    assert book.available_copies == 2
    assert user.active_borrowings_count() == 0
    
    # Step 2: Borrow a book
    borrowing = user.borrow_book(book)
    db_session.commit()
    
    assert borrowing is not None
    assert borrowing.status == 'borrowed'
    assert book.available_copies == 1
    assert user.active_borrowings_count() == 1
    
    # Step 3: Try to borrow the same book again
    with pytest.raises(ValueError):
        user.borrow_book(book)
    
    # Step 4: Renew the book
    original_due_date = borrowing.due_date
    borrowing.renew()
    db_session.commit()
    
    assert borrowing.due_date > original_due_date
    assert borrowing.renewal_count == 1
    
    # Step 5: Return the book
    borrowing.return_book()
    db_session.commit()
    
    assert borrowing.status == 'returned'
    assert borrowing.return_date is not None
    assert book.available_copies == 2
    assert user.active_borrowings_count() == 0

def test_overdue_borrowing_flow(db_session):
    """Test the overdue book borrowing flow."""
    # Create test data
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    book.add_copies(1)
    db_session.commit()
    
    # Create an overdue borrowing
    borrowing = user.borrow_book(book)
    borrowing.borrow_date = datetime.utcnow() - timedelta(days=30)
    borrowing.due_date = datetime.utcnow() - timedelta(days=15)
    db_session.commit()
    
    # Check overdue status
    assert borrowing.is_overdue() is True
    assert borrowing.days_overdue() == 15
    
    # Calculate fine
    fine = borrowing.calculate_fine()
    assert fine.amount == 15.00  # 15 days overdue * $1 per day
    
    # Try to renew overdue book
    with pytest.raises(ValueError):
        borrowing.renew()
    
    # Return the book
    borrowing.return_book()
    db_session.commit()
    
    assert borrowing.status == 'returned'
    assert book.available_copies == 1

def test_user_borrowing_limits(db_session):
    """Test user borrowing limits and restrictions."""
    # Create test data
    user = create_test_user(db_session)
    books = [create_test_book(db_session) for _ in range(5)]
    for book in books:
        book.add_copies(1)
    db_session.commit()
    
    # Borrow books up to limit
    borrowings = []
    for book in books[:3]:  # Assuming limit is 3
        borrowing = user.borrow_book(book)
        borrowings.append(borrowing)
    db_session.commit()
    
    assert user.active_borrowings_count() == 3
    
    # Try to borrow beyond limit
    with pytest.raises(ValueError):
        user.borrow_book(books[3])
    
    # Return one book
    borrowings[0].return_book()
    db_session.commit()
    
    assert user.active_borrowings_count() == 2
    
    # Now should be able to borrow again
    borrowing = user.borrow_book(books[3])
    db_session.commit()
    
    assert borrowing.status == 'borrowed'
    assert user.active_borrowings_count() == 3

def test_book_availability_tracking(db_session):
    """Test book availability tracking across multiple operations."""
    # Create test data
    user1 = create_test_user(db_session)
    user2 = create_test_user(db_session)
    book = create_test_book(db_session)
    book.add_copies(2)
    db_session.commit()
    
    # Initial state
    assert book.available_copies == 2
    assert book.is_available() is True
    
    # First user borrows
    borrowing1 = user1.borrow_book(book)
    db_session.commit()
    
    assert book.available_copies == 1
    assert book.is_available() is True
    
    # Second user borrows
    borrowing2 = user2.borrow_book(book)
    db_session.commit()
    
    assert book.available_copies == 0
    assert book.is_available() is False
    
    # First user returns
    borrowing1.return_book()
    db_session.commit()
    
    assert book.available_copies == 1
    assert book.is_available() is True
    
    # Second user returns
    borrowing2.return_book()
    db_session.commit()
    
    assert book.available_copies == 2
    assert book.is_available() is True

def test_borrowing_validation(db_session):
    """Test borrowing validation rules."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Test borrowing with invalid dates
    with pytest.raises(ValueError):
        Borrowing(
            user_id=user.user_id,
            book_id=book.book_id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() - timedelta(days=1),  # Due date before borrow date
            status='borrowed'
        )
    
    # Test borrowing with no available copies
    book.total_copies = 0
    db_session.commit()
    
    with pytest.raises(ValueError):
        Borrowing(
            user_id=user.user_id,
            book_id=book.book_id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
            status='borrowed'
        )

def test_borrowing_renewal_limits(db_session):
    """Test borrowing renewal limits and restrictions."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    # Test maximum renewals
    borrowing.renewal_count = 3  # Assuming max renewals is 3
    with pytest.raises(ValueError):
        borrowing.renew()
    
    # Test renewal of returned book
    borrowing.return_book()
    db_session.commit()
    
    with pytest.raises(ValueError):
        borrowing.renew()

def test_fine_calculation_edge_cases(db_session):
    """Test fine calculation edge cases."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Test fine for book returned exactly on due date
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow() - timedelta(days=14),
        due_date=datetime.utcnow(),
        return_date=datetime.utcnow(),
        status='returned'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    assert borrowing.is_overdue() is False
    assert borrowing.days_overdue() == 0
    
    # Test fine for book returned before due date
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow() - timedelta(days=14),
        due_date=datetime.utcnow() + timedelta(days=1),
        return_date=datetime.utcnow(),
        status='returned'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    assert borrowing.is_overdue() is False
    assert borrowing.days_overdue() == 0

def test_user_borrowing_restrictions(db_session):
    """Test user borrowing restrictions."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Test borrowing with existing overdue books
    overdue_borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow() - timedelta(days=30),
        due_date=datetime.utcnow() - timedelta(days=15),
        status='borrowed'
    )
    db_session.add(overdue_borrowing)
    db_session.commit()
    
    with pytest.raises(ValueError):
        Borrowing(
            user_id=user.user_id,
            book_id=book.book_id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
            status='borrowed'
        )
    
    # Test borrowing with unpaid fines
    fine = Fine(
        user_id=user.user_id,
        borrowing_id=overdue_borrowing.borrowing_id,
        amount=15.00,
        reason='overdue',
        status='pending'
    )
    db_session.add(fine)
    db_session.commit()
    
    with pytest.raises(ValueError):
        Borrowing(
            user_id=user.user_id,
            book_id=book.book_id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
            status='borrowed'
        )

def test_book_availability_tracking(db_session):
    """Test book availability tracking edge cases."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Test book with no copies
    book.total_copies = 0
    db_session.commit()
    
    assert book.copies_available == 0
    assert book.is_available() is False
    
    # Test book with all copies borrowed
    book.total_copies = 2
    borrowing1 = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    borrowing2 = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add_all([borrowing1, borrowing2])
    db_session.commit()
    
    assert book.copies_available == 0
    assert book.is_available() is False
    
    # Test book with some copies available
    borrowing1.return_book()
    db_session.commit()
    
    assert book.copies_available == 1
    assert book.is_available() is True

def test_borrowing_status_transitions(db_session):
    """Test borrowing status transition rules."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    borrowing = Borrowing(
        user_id=user.user_id,
        book_id=book.book_id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    # Test invalid status transitions
    with pytest.raises(ValueError):
        borrowing.status = 'invalid_status'
        db_session.commit()
    
    # Test return of already returned book
    borrowing.return_book()
    db_session.commit()
    
    with pytest.raises(ValueError):
        borrowing.return_book()
    
    # Test borrowing of returned book
    with pytest.raises(ValueError):
        borrowing.status = 'borrowed'
        db_session.commit() 