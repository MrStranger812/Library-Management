import pytest
from models.borrowing import Borrowing
from models.user import User
from models.book import Book
from datetime import datetime, timedelta
from tests.fixtures.test_data import create_test_user, create_test_book

def test_create_borrowing(db_session):
    """Test borrowing creation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    assert borrowing.id is not None
    assert borrowing.user_id == user.id
    assert borrowing.book_id == book.id
    assert borrowing.status == 'borrowed'
    assert borrowing.return_date is None

def test_borrowing_dates_validation(db_session):
    """Test borrowing dates validation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    with pytest.raises(ValueError):
        Borrowing(
            user_id=user.id,
            book_id=book.id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() - timedelta(days=1),  # Due date before borrow date
            status='borrowed'
        )

def test_borrowing_status_transitions(db_session):
    """Test borrowing status transitions."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    assert borrowing.status == 'borrowed'
    
    # Test return
    borrowing.return_book()
    db_session.commit()
    
    assert borrowing.status == 'returned'
    assert borrowing.return_date is not None
    
    # Test invalid status transition
    with pytest.raises(ValueError):
        borrowing.return_book()  # Cannot return an already returned book

def test_borrowing_overdue_calculation(db_session):
    """Test overdue calculation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Create an overdue borrowing
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        borrow_date=datetime.utcnow() - timedelta(days=30),
        due_date=datetime.utcnow() - timedelta(days=15),
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    assert borrowing.is_overdue() is True
    assert borrowing.days_overdue() == 15
    
    # Return the book
    borrowing.return_book()
    db_session.commit()
    
    assert borrowing.is_overdue() is False
    assert borrowing.days_overdue() == 0

def test_borrowing_fine_calculation(db_session):
    """Test fine calculation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Create an overdue borrowing
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        borrow_date=datetime.utcnow() - timedelta(days=30),
        due_date=datetime.utcnow() - timedelta(days=15),
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    # Calculate fine (assuming $1 per day)
    fine = borrowing.calculate_fine()
    assert fine == 15.00  # 15 days overdue * $1 per day

def test_borrowing_renewal(db_session):
    """Test book renewal functionality."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    original_due_date = borrowing.due_date
    
    # Renew the book
    borrowing.renew()
    db_session.commit()
    
    assert borrowing.due_date > original_due_date
    assert borrowing.renewal_count == 1
    
    # Test maximum renewals
    borrowing.renewal_count = 3  # Assuming max renewals is 3
    with pytest.raises(ValueError):
        borrowing.renew()

def test_borrowing_user_limits(db_session):
    """Test user borrowing limits."""
    user = create_test_user(db_session)
    book1 = create_test_book(db_session)
    book2 = create_test_book(db_session)
    
    # Create first borrowing
    borrowing1 = Borrowing(
        user_id=user.id,
        book_id=book1.id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing1)
    db_session.commit()
    
    # Create second borrowing
    borrowing2 = Borrowing(
        user_id=user.id,
        book_id=book2.id,
        borrow_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=14),
        status='borrowed'
    )
    db_session.add(borrowing2)
    db_session.commit()
    
    # Test active borrowings count
    assert user.active_borrowings_count() == 2
    
    # Return one book
    borrowing1.return_book()
    db_session.commit()
    
    assert user.active_borrowings_count() == 1

def test_borrowing_history(db_session):
    """Test borrowing history tracking."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
    # Create and return a borrowing
    borrowing = Borrowing(
        user_id=user.id,
        book_id=book.id,
        borrow_date=datetime.utcnow() - timedelta(days=30),
        due_date=datetime.utcnow() - timedelta(days=15),
        return_date=datetime.utcnow() - timedelta(days=10),
        status='returned'
    )
    db_session.add(borrowing)
    db_session.commit()
    
    # Test history retrieval
    history = user.get_borrowing_history()
    assert len(history) == 1
    assert history[0].id == borrowing.id
    assert history[0].status == 'returned' 