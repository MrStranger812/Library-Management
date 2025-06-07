"""
Borrowing models for the Library Management System.
Includes Borrowing, Fine, FinePayment, and Reservation models.
"""

from models import db
from datetime import UTC, datetime, timedelta
from sqlalchemy import CheckConstraint, Index

class Borrowing(db.Model):
    """Model for book borrowings."""
    __tablename__ = 'borrowings'
    
    borrowing_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    copy_id = db.Column(db.Integer, db.ForeignKey('book_copies.copy_id', ondelete='SET NULL'), index=True)
    borrow_date = db.Column(db.Date, nullable=False, default=datetime.now(UTC).date, index=True)
    due_date = db.Column(db.Date, nullable=False, index=True)
    return_date = db.Column(db.Date, index=True)
    status = db.Column(db.Enum('borrowed', 'returned', 'overdue', 'lost'), default='borrowed', index=True)
    fine_amount = db.Column(db.Numeric(10, 2), default=0.00)
    fine_paid = db.Column(db.Boolean, default=False, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    user = db.relationship('User', backref=db.backref('borrowings', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('borrowings', lazy='dynamic'))
    copy = db.relationship('BookCopy', backref=db.backref('borrowings', lazy='dynamic'))
    fines = db.relationship('Fine', backref='borrowing', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('due_date > borrow_date', name='chk_due_after_borrow'),
        CheckConstraint('return_date >= borrow_date', name='chk_return_after_borrow'),
        CheckConstraint('fine_amount >= 0', name='chk_fine_positive'),
        Index('idx_borrowing_status_dates', 'status', 'borrow_date', 'due_date', 'return_date')
    )

    def __init__(self, user_id, book_id, due_date, copy_id=None, notes=None):
        """Initialize a new borrowing."""
        self.user_id = user_id
        self.book_id = book_id
        self.due_date = due_date
        self.copy_id = copy_id
        self.notes = notes
        self.status = 'borrowed'
        self.fine_amount = 0.00
        self.fine_paid = False

    @classmethod
    def get_by_id(cls, borrowing_id):
        """Get a borrowing record by its ID."""
        return cls.query.get(borrowing_id)

    @classmethod
    def get_user_borrowings(cls, user_id, status=None):
        """Get all borrowings for a specific user, optionally filtered by status."""
        query = cls.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.borrow_date.desc()).all()

    @classmethod
    def get_overdue_borrowings(cls):
        """Get all overdue borrowings."""
        return cls.query.filter(
            cls.status == 'borrowed',
            cls.due_date < datetime.now(UTC).date()
        ).order_by(cls.due_date.asc()).all()

    @classmethod
    def get_active_borrowings(cls):
        """Get all active (borrowed) borrowings."""
        return cls.query.filter_by(status='borrowed').order_by(cls.due_date.asc()).all()

    @classmethod
    def get_borrowings_by_date_range(cls, start_date, end_date):
        """Get all borrowings within a date range."""
        return cls.query.filter(
            cls.borrow_date >= start_date,
            cls.borrow_date <= end_date
        ).order_by(cls.borrow_date.desc()).all()

    def calculate_fine(self):
        """Calculate fine for overdue book."""
        if self.status == 'borrowed' and self.due_date < datetime.now(UTC).date():
            days_overdue = (datetime.now(UTC).date() - self.due_date).days
            self.fine_amount = days_overdue * 1.0  # $1 per day
            self.status = 'overdue'
            db.session.commit()
            return self.fine_amount
        return 0.00

    def return_book(self):
        """Mark book as returned and update related records."""
        self.return_date = datetime.now(UTC).date()
        self.status = 'returned'
        if self.copy:
            self.copy.is_available = True
            self.copy.updated_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def mark_as_lost(self):
        """Mark book as lost and update related records."""
        self.status = 'lost'
        self.return_date = datetime.now(UTC).date()
        self.fine_amount = 50.00  # Standard lost book fee
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def extend_due_date(self, days=7):
        """Extend the due date by specified number of days."""
        if self.status == 'borrowed':
            self.due_date += timedelta(days=days)
            self.updated_at = datetime.now(UTC)
            db.session.commit()
            return True
        return False

    def to_dict(self):
        """Convert borrowing to dictionary."""
        return {
            'borrowing_id': self.borrowing_id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'copy_id': self.copy_id,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'fine_amount': float(self.fine_amount) if self.fine_amount else 0.00,
            'fine_paid': self.fine_paid,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book': self.book.to_dict() if self.book else None,
            'user': self.user.to_dict() if self.user else None
        }

    def __repr__(self):
        """String representation of the borrowing."""
        return f'<Borrowing {self.borrowing_id}: {self.book.title if self.book else "Unknown Book"}>'

class Fine(db.Model):
    """Model for fines."""
    __tablename__ = 'fines'
    
    fine_id = db.Column(db.Integer, primary_key=True)
    borrowing_id = db.Column(db.Integer, db.ForeignKey('borrowings.borrowing_id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    paid_at = db.Column(db.DateTime, index=True)
    is_paid = db.Column(db.Boolean, default=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    payments = db.relationship('FinePayment', backref='fine', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('amount >= 0', name='chk_fine_amount_positive'),
    )

    def __init__(self, borrowing_id, amount, reason):
        """Initialize a new fine."""
        self.borrowing_id = borrowing_id
        self.amount = amount
        self.reason = reason
        self.is_paid = False

    @classmethod
    def get_unpaid_fines(cls):
        """Get all unpaid fines."""
        return cls.query.filter_by(is_paid=False).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_user_fines(cls, user_id):
        """Get all fines for a specific user."""
        return cls.query.join(Borrowing).filter(Borrowing.user_id == user_id).order_by(cls.created_at.desc()).all()

    def mark_as_paid(self):
        """Mark the fine as paid."""
        self.is_paid = True
        self.paid_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def to_dict(self):
        """Convert fine to dictionary."""
        return {
            'fine_id': self.fine_id,
            'borrowing_id': self.borrowing_id,
            'amount': float(self.amount) if self.amount else 0.00,
            'reason': self.reason,
            'is_paid': self.is_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'payments': [payment.to_dict() for payment in self.payments]
        }

    def __repr__(self):
        """String representation of the fine."""
        return f'<Fine {self.fine_id}: ${self.amount}>'

class FinePayment(db.Model):
    """Model for fine payments."""
    __tablename__ = 'fine_payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    fine_id = db.Column(db.Integer, db.ForeignKey('fines.fine_id', ondelete='CASCADE'), nullable=False, index=True)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum('cash', 'card', 'online', 'cheque'), nullable=False, index=True)
    payment_reference = db.Column(db.String(100))
    paid_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    paid_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    paid_by_user = db.relationship('User', backref=db.backref('fine_payments', lazy='dynamic'))

    __table_args__ = (
        CheckConstraint('amount_paid > 0', name='chk_payment_amount_positive'),
    )

    def __init__(self, fine_id, amount_paid, payment_method, paid_by=None, payment_reference=None, notes=None):
        """Initialize a new fine payment."""
        self.fine_id = fine_id
        self.amount_paid = amount_paid
        self.payment_method = payment_method
        self.paid_by = paid_by
        self.payment_reference = payment_reference
        self.notes = notes

    @classmethod
    def get_payments_by_fine(cls, fine_id):
        """Get all payments for a specific fine."""
        return cls.query.filter_by(fine_id=fine_id).order_by(cls.paid_at.desc()).all()

    @classmethod
    def get_payments_by_user(cls, user_id):
        """Get all payments made by a specific user."""
        return cls.query.filter_by(paid_by=user_id).order_by(cls.paid_at.desc()).all()

    def to_dict(self):
        """Convert payment to dictionary."""
        return {
            'payment_id': self.payment_id,
            'fine_id': self.fine_id,
            'amount_paid': float(self.amount_paid) if self.amount_paid else 0.00,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'paid_by': self.paid_by,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the payment."""
        return f'<FinePayment {self.payment_id}: ${self.amount_paid}>'

class Reservation(db.Model):
    """Model for book reservations."""
    __tablename__ = 'reservations'
    
    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    reservation_date = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    expiry_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.Enum('pending', 'fulfilled', 'cancelled', 'expired'), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    notes = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', backref=db.backref('reservations', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('reservations', lazy='dynamic'))

    __table_args__ = (
        CheckConstraint('expiry_date > reservation_date', name='chk_expiry_after_reservation'),
        Index('idx_reservation_status_dates', 'status', 'reservation_date', 'expiry_date')
    )

    def __init__(self, user_id, book_id, expiry_date, notes=None):
        """Initialize a new reservation."""
        self.user_id = user_id
        self.book_id = book_id
        self.expiry_date = expiry_date
        self.notes = notes
        self.status = 'pending'

    @classmethod
    def get_by_id(cls, reservation_id):
        """Get a reservation by its ID."""
        return cls.query.get(reservation_id)

    @classmethod
    def get_user_reservations(cls, user_id, status=None):
        """Get all reservations for a specific user, optionally filtered by status."""
        query = cls.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.reservation_date.desc()).all()

    @classmethod
    def get_pending_reservations(cls, book_id):
        """Get all pending reservations for a specific book."""
        return cls.query.filter_by(
            book_id=book_id,
            status='pending'
        ).order_by(cls.reservation_date.asc()).all()

    @classmethod
    def get_expired_reservations(cls):
        """Get all expired reservations."""
        return cls.query.filter(
            cls.status == 'pending',
            cls.expiry_date < datetime.now(UTC).date()
        ).all()

    def cancel(self):
        """Cancel the reservation."""
        self.status = 'cancelled'
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def fulfill(self):
        """Mark the reservation as fulfilled."""
        self.status = 'fulfilled'
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def check_expiry(self):
        """Check if the reservation has expired."""
        if self.status == 'pending' and self.expiry_date < datetime.now(UTC).date():
            self.status = 'expired'
            self.updated_at = datetime.now(UTC)
            db.session.commit()
            return True
        return False

    def to_dict(self):
        """Convert reservation to dictionary."""
        return {
            'reservation_id': self.reservation_id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'reservation_date': self.reservation_date.isoformat() if self.reservation_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book': self.book.to_dict() if self.book else None,
            'user': self.user.to_dict() if self.user else None
        }

    def __repr__(self):
        """String representation of the reservation."""
        return f'<Reservation {self.reservation_id}: {self.book.title if self.book else "Unknown Book"}>'