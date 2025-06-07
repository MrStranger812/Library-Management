import pytest
from models.fine import Fine
from models.user import User
from models.borrowing import Borrowing
from models.book import Book
from datetime import datetime, timedelta
from tests.fixtures.test_data import create_test_user, create_test_book

def test_create_fine(db_session):
    """Test fine creation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    fine = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=15.00,
        reason='overdue',
        status='pending'
    )
    db_session.add(fine)
    db_session.commit()
    
    assert fine.fine_id is not None
    assert fine.user_id == user.user_id
    assert fine.borrowing_id == borrowing.borrowing_id
    assert fine.amount == 15.00
    assert fine.status == 'pending'

def test_fine_amount_validation(db_session):
    """Test fine amount validation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    with pytest.raises(ValueError):
        Fine(
            user_id=user.user_id,
            borrowing_id=borrowing.borrowing_id,
            amount=-10.00,  # Negative amount
            reason='overdue',
            status='pending'
        )

def test_fine_status_transitions(db_session):
    """Test fine status transitions."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    fine = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=15.00,
        reason='overdue',
        status='pending'
    )
    db_session.add(fine)
    db_session.commit()
    
    assert fine.status == 'pending'
    
    # Test payment
    fine.pay()
    db_session.commit()
    
    assert fine.status == 'paid'
    assert fine.payment_date is not None
    
    # Test invalid status transition
    with pytest.raises(ValueError):
        fine.pay()  # Cannot pay an already paid fine

def test_fine_payment_tracking(db_session):
    """Test fine payment tracking."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    fine = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=15.00,
        reason='overdue',
        status='pending'
    )
    db_session.add(fine)
    db_session.commit()
    
    # Test partial payment
    fine.pay(amount=5.00)
    db_session.commit()
    
    assert fine.status == 'partial'
    assert fine.amount_paid == 5.00
    assert fine.remaining_amount == 10.00
    
    # Test complete payment
    fine.pay(amount=10.00)
    db_session.commit()
    
    assert fine.status == 'paid'
    assert fine.amount_paid == 15.00
    assert fine.remaining_amount == 0.00

def test_fine_reason_validation(db_session):
    """Test fine reason validation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    with pytest.raises(ValueError):
        Fine(
            user_id=user.user_id,
            borrowing_id=borrowing.borrowing_id,
            amount=15.00,
            reason='invalid_reason',  # Invalid reason
            status='pending'
        )

def test_fine_user_limits(db_session):
    """Test user fine limits."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    # Test total fines
    assert user.total_fines() == 25.00
    assert user.pending_fines() == 25.00
    
    # Pay one fine
    fine1.pay()
    db_session.commit()
    
    assert user.total_fines() == 25.00
    assert user.pending_fines() == 10.00

def test_fine_history(db_session):
    """Test fine history tracking."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    
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
    
    fine = Fine(
        user_id=user.user_id,
        borrowing_id=borrowing.borrowing_id,
        amount=15.00,
        reason='overdue',
        status='pending'
    )
    db_session.add(fine)
    db_session.commit()
    
    # Test fine history
    history = user.get_fine_history()
    assert len(history) == 1
    assert history[0].amount == 15.00
    assert history[0].status == 'pending' 