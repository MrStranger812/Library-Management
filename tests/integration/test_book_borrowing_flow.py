import pytest
from datetime import datetime, timedelta
from tests.fixtures.test_data import create_test_user, create_test_book

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

def test_concurrent_borrowing_flow(db_session):
    """Test concurrent book borrowing scenarios."""
    # Create test data
    user = create_test_user(db_session)
    book1 = create_test_book(db_session)
    book2 = create_test_book(db_session)
    book1.add_copies(1)
    book2.add_copies(1)
    db_session.commit()
    
    # Borrow first book
    borrowing1 = user.borrow_book(book1)
    db_session.commit()
    
    assert borrowing1.status == 'borrowed'
    assert book1.available_copies == 0
    
    # Borrow second book
    borrowing2 = user.borrow_book(book2)
    db_session.commit()
    
    assert borrowing2.status == 'borrowed'
    assert book2.available_copies == 0
    assert user.active_borrowings_count() == 2
    
    # Try to borrow a book with no copies
    with pytest.raises(ValueError):
        user.borrow_book(book1)
    
    # Return first book
    borrowing1.return_book()
    db_session.commit()
    
    assert borrowing1.status == 'returned'
    assert book1.available_copies == 1
    assert user.active_borrowings_count() == 1
    
    # Borrow first book again
    borrowing3 = user.borrow_book(book1)
    db_session.commit()
    
    assert borrowing3.status == 'borrowed'
    assert book1.available_copies == 0
    assert user.active_borrowings_count() == 2

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