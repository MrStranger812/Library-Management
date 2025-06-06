import pytest
from models.fine import Fine
from models.borrowing import Borrowing
from datetime import datetime, timedelta
from tests.fixtures.test_data import create_test_user, create_test_book, create_test_borrowing

def test_create_fine(db_session):
    """Test fine creation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    borrowing = create_test_borrowing(db_session, user, book)
    
    fine = Fine(
        borrowing_id=borrowing.id,
        amount=10.00,
        status='unpaid',
        created_at=datetime.utcnow()
    )
    db_session.add(fine)
    db_session.commit()
    
    assert fine.id is not None
    assert fine.borrowing_id == borrowing.id
    assert fine.amount == 10.00
    assert fine.status == 'unpaid'
    assert fine.paid_at is None

def test_fine_amount_validation(db_session):
    """Test fine amount validation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    borrowing = create_test_borrowing(db_session, user, book)
    
    with pytest.raises(ValueError):
        Fine(
            borrowing_id=borrowing.id,
            amount=-10.00,  # Negative amount
            status='unpaid'
        )

def test_fine_status_transitions(db_session):
    """Test fine status transitions."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    borrowing = create_test_borrowing(db_session, user, book)
    
    fine = Fine(
        borrowing_id=borrowing.id,
        amount=10.00,
        status='unpaid'
    )
    db_session.add(fine)
    db_session.commit()
    
    assert fine.status == 'unpaid'
    
    # Test payment
    fine.pay()
    db_session.commit()
    
    assert fine.status == 'paid'
    assert fine.paid_at is not None
    
    # Test invalid status transition
    with pytest.raises(ValueError):
        fine.pay()  # Cannot pay an already paid fine

def test_fine_calculation(db_session):
    """Test fine calculation based on overdue days."""
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
    
    # Calculate fine
    fine = Fine.calculate_for_borrowing(borrowing)
    assert fine.amount == 15.00  # 15 days overdue * $1 per day

def test_fine_payment_tracking(db_session):
    """Test fine payment tracking."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    borrowing = create_test_borrowing(db_session, user, book)
    
    fine = Fine(
        borrowing_id=borrowing.id,
        amount=10.00,
        status='unpaid'
    )
    db_session.add(fine)
    db_session.commit()
    
    # Test payment tracking
    payment_date = datetime.utcnow()
    fine.pay(payment_date=payment_date)
    db_session.commit()
    
    assert fine.status == 'paid'
    assert fine.paid_at == payment_date
    assert fine.is_paid() is True

def test_fine_user_totals(db_session):
    """Test user fine totals calculation."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    borrowing = create_test_borrowing(db_session, user, book)
    
    # Create multiple fines
    fine1 = Fine(
        borrowing_id=borrowing.id,
        amount=10.00,
        status='unpaid'
    )
    fine2 = Fine(
        borrowing_id=borrowing.id,
        amount=15.00,
        status='unpaid'
    )
    db_session.add_all([fine1, fine2])
    db_session.commit()
    
    # Test total calculation
    totals = user.get_fine_totals()
    assert totals['total'] == 25.00
    assert totals['unpaid'] == 25.00
    assert totals['paid'] == 0.00
    
    # Pay one fine
    fine1.pay()
    db_session.commit()
    
    totals = user.get_fine_totals()
    assert totals['total'] == 25.00
    assert totals['unpaid'] == 15.00
    assert totals['paid'] == 10.00

def test_fine_waiver(db_session):
    """Test fine waiver functionality."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    borrowing = create_test_borrowing(db_session, user, book)
    
    fine = Fine(
        borrowing_id=borrowing.id,
        amount=10.00,
        status='unpaid'
    )
    db_session.add(fine)
    db_session.commit()
    
    # Test waiver
    fine.waive('Test waiver reason')
    db_session.commit()
    
    assert fine.status == 'waived'
    assert fine.waiver_reason == 'Test waiver reason'
    assert fine.is_paid() is True

def test_fine_payment_history(db_session):
    """Test fine payment history tracking."""
    user = create_test_user(db_session)
    book = create_test_book(db_session)
    borrowing = create_test_borrowing(db_session, user, book)
    
    fine = Fine(
        borrowing_id=borrowing.id,
        amount=10.00,
        status='unpaid'
    )
    db_session.add(fine)
    db_session.commit()
    
    # Add payment history
    fine.add_payment_history(5.00, 'partial payment')
    db_session.commit()
    
    assert len(fine.payment_history) == 1
    assert fine.payment_history[0].amount == 5.00
    assert fine.payment_history[0].note == 'partial payment'
    
    # Complete payment
    fine.add_payment_history(5.00, 'final payment')
    fine.pay()
    db_session.commit()
    
    assert len(fine.payment_history) == 2
    assert fine.status == 'paid' 