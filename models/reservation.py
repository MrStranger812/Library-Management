"""
Reservation model for the Library Management System.
Handles book reservations and their lifecycle.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import Index, CheckConstraint
from sqlalchemy.orm import relationship

class Reservation(db.Model):
    """Model representing a book reservation in the library system."""
    
    __tablename__ = 'reservations'
    
    # Columns
    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(UTC).date())
    status = db.Column(db.String(20), nullable=False, default='pending')
    notification_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    # Indexes
    __table_args__ = (
        Index('idx_reservation_user', 'user_id'),
        Index('idx_reservation_book', 'book_id'),
        Index('idx_reservation_status', 'status'),
        Index('idx_reservation_date', 'reservation_date'),
        CheckConstraint("status IN ('pending', 'fulfilled', 'cancelled', 'expired')", name='valid_reservation_status'),
        {'extend_existing': True}
    )
    
    # Relationships
    user = relationship('User', backref=db.backref('reservations', lazy='dynamic'))
    book = relationship('Book', backref=db.backref('reservations', lazy='dynamic'))
    
    def __init__(self, user_id, book_id, status='pending'):
        """
        Initialize a new reservation.
        
        Args:
            user_id (int): ID of the user making the reservation
            book_id (int): ID of the book being reserved
            status (str): Initial status of the reservation
        """
        self.user_id = user_id
        self.book_id = book_id
        self.status = status
        self.reservation_date = datetime.now(UTC).date()
        self.notification_sent = False
    
    @classmethod
    def create_reservation(cls, user_id, book_id):
        """
        Create a new book reservation.
        
        Args:
            user_id (int): ID of the user making the reservation
            book_id (int): ID of the book being reserved
            
        Returns:
            tuple: (success (bool), message (str))
        """
        from models.book import Book
        
        # Check if book exists and is unavailable
        book = Book.query.get(book_id)
        if not book:
            return False, "Book not found"
        
        if book.copies_available > 0:
            return False, "Book is available for borrowing, no need to reserve"
        
        # Check if user already has a pending reservation for this book
        existing_reservation = cls.query.filter_by(
            user_id=user_id,
            book_id=book_id,
            status='pending'
        ).first()
        
        if existing_reservation:
            return False, "You already have a pending reservation for this book"
        
        # Create new reservation
        reservation = cls(user_id=user_id, book_id=book_id)
        db.session.add(reservation)
        
        try:
            db.session.commit()
            return True, "Book reserved successfully. You will be notified when it becomes available."
        except Exception as e:
            db.session.rollback()
            return False, f"Error creating reservation: {str(e)}"
    
    @classmethod
    def get_user_reservations(cls, user_id, status=None):
        """
        Get all reservations for a specific user.
        
        Args:
            user_id (int): ID of the user
            status (str, optional): Filter by reservation status
            
        Returns:
            list: List of Reservation objects
        """
        query = cls.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.reservation_date.desc()).all()
    
    @classmethod
    def get_book_reservations(cls, book_id, status=None):
        """
        Get all reservations for a specific book.
        
        Args:
            book_id (int): ID of the book
            status (str, optional): Filter by reservation status
            
        Returns:
            list: List of Reservation objects
        """
        query = cls.query.filter_by(book_id=book_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.reservation_date.asc()).all()
    
    def cancel(self):
        """
        Cancel this reservation.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.status != 'pending':
            return False
        
        self.status = 'cancelled'
        self.updated_at = datetime.now(UTC)
        
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def fulfill(self):
        """
        Mark this reservation as fulfilled.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.status != 'pending':
            return False
        
        self.status = 'fulfilled'
        self.updated_at = datetime.now(UTC)
        
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    def to_dict(self):
        """
        Convert reservation to dictionary.
        
        Returns:
            dict: Dictionary representation of the reservation
        """
        return {
            'reservation_id': self.reservation_id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'reservation_date': self.reservation_date.isoformat(),
            'status': self.status,
            'notification_sent': self.notification_sent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        """String representation of the reservation."""
        return f"<Reservation {self.reservation_id}: {self.user_id} -> {self.book_id} ({self.status})>"