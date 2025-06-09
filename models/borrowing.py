"""
Borrowing models for the Library Management System.
Includes Borrowing and Reservation models.
"""

from models import db
from datetime import UTC, datetime, timedelta, date
from sqlalchemy import CheckConstraint, Index, func
from models.fine import Fine

class Borrowing(db.Model):
    """Model for book borrowings."""
    __tablename__ = 'borrowings'
    
    borrowing_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    copy_id = db.Column(db.Integer, db.ForeignKey('book_copies.copy_id', ondelete='CASCADE'), nullable=False, index=True)
    borrow_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    due_date = db.Column(db.Date, nullable=False, index=True)
    return_date = db.Column(db.Date, nullable=True, index=True)
    status = db.Column(db.String(20), nullable=False, default='borrowed', index=True)
    renewal_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    user = db.relationship('User', back_populates='borrowings')
    book = db.relationship('Book', back_populates='borrowings')
    copy = db.relationship('BookCopy', back_populates='borrowings')
    fines = db.relationship('Fine', back_populates='borrowing', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('due_date > borrow_date', name='chk_due_after_borrow'),
        CheckConstraint('return_date >= borrow_date', name='chk_return_after_borrow'),
        Index('idx_borrowing_status_dates', 'status', 'borrow_date', 'due_date', 'return_date')
    )

    def __init__(self, user_id, book_id, copy_id, borrow_date=None, due_date=None, status='borrowed'):
        """Initialize a new borrowing."""
        self.user_id = user_id
        self.book_id = book_id
        self.copy_id = copy_id
        self.borrow_date = borrow_date or date.today()
        self.due_date = due_date or (date.today() + timedelta(days=14))
        self.status = status
        self.renewal_count = 0

    @classmethod
    def get_by_id(cls, borrowing_id):
        """Get a borrowing by its ID."""
        return cls.query.get(borrowing_id)

    @classmethod
    def get_user_borrowings(cls, user_id):
        """Get all borrowings for a specific user."""
        return cls.query.filter_by(user_id=user_id).order_by(cls.borrow_date.desc()).all()

    @classmethod
    def get_active_borrowings(cls, user_id):
        """Get active borrowings for a specific user."""
        return cls.query.filter_by(
            user_id=user_id,
            status='borrowed'
        ).order_by(cls.due_date.asc()).all()

    @classmethod
    def get_overdue_borrowings(cls):
        """Get all overdue borrowings."""
        return cls.query.filter(
            cls.status == 'borrowed',
            cls.due_date < date.today()
        ).order_by(cls.due_date.asc()).all()

    def is_overdue(self):
        """Check if the borrowing is overdue."""
        return self.status == 'borrowed' and self.due_date < date.today()

    def days_overdue(self):
        """Calculate days overdue."""
        if not self.is_overdue():
            return 0
        return (date.today() - self.due_date).days

    def calculate_fine(self):
        """Calculate fine for overdue book."""
        if not self.is_overdue():
            return 0
        
        days_overdue = self.days_overdue()
        fine_amount = days_overdue * 1.00  # $1 per day
        
        # Create fine record if it doesn't exist
        existing_fine = Fine.query.filter_by(
            borrowing_id=self.borrowing_id,
            status='pending'
        ).first()
        
        if existing_fine:
            return existing_fine
        
        fine = Fine(
            borrowing_id=self.borrowing_id,
            amount=fine_amount,
            reason='overdue'
        )
        db.session.add(fine)
        db.session.commit()
        return fine

    def renew(self):
        """Renew the borrowing."""
        if self.status != 'borrowed':
            raise ValueError("Only borrowed books can be renewed")
        
        if self.is_overdue():
            raise ValueError("Overdue books cannot be renewed")
        
        if self.renewal_count >= 3:  # Maximum 3 renewals
            raise ValueError("Maximum renewal limit reached")
        
        self.due_date = date.today() + timedelta(days=14)
        self.renewal_count += 1
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def return_book(self):
        """Return the borrowed book."""
        if self.status != 'borrowed':
            raise ValueError("Book is not currently borrowed")
        
        self.status = 'returned'
        self.return_date = date.today()
        self.updated_at = datetime.now(UTC)
        
        # Update book copy availability
        self.copy.is_available = True
        
        # Update book availability count
        self.book.copies_available += 1
        
        db.session.commit()

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
            'renewal_count': self.renewal_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_overdue': self.is_overdue(),
            'days_overdue': self.days_overdue(),
            'book': self.book.to_dict() if self.book else None,
            'copy': self.copy.to_dict() if self.copy else None,
            'fines': [fine.to_dict() for fine in self.fines]
        }

    def __repr__(self):
        """String representation of the borrowing."""
        return f'<Borrowing {self.borrowing_id}: {self.book.title if self.book else None}>'

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