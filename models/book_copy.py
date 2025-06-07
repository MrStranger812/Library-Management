"""
BookCopy model for managing individual copies of books in the library system.
"""

from datetime import datetime, UTC
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from models import db

class BookCopy(db.Model):
    """Model representing an individual copy of a book."""
    
    __tablename__ = 'book_copies'
    __table_args__ = {'extend_existing': True}
    
    copy_id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    barcode = Column(String(50), unique=True, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    condition = Column(String(20), default='good', nullable=False)
    location = Column(String(50))
    notes = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    
    # Relationships
    book = relationship('Book', back_populates='copies')
    borrowings = relationship('Borrowing', back_populates='copy')
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "condition IN ('new', 'good', 'fair', 'poor', 'damaged')",
            name='valid_condition'
        ),
        {'extend_existing': True}
    )
    
    def __init__(self, book_id, barcode, condition='good', location=None, notes=None):
        """Initialize a new book copy.
        
        Args:
            book_id (int): ID of the book this copy belongs to
            barcode (str): Unique barcode for this copy
            condition (str): Condition of the book copy
            location (str, optional): Location of the book copy
            notes (str, optional): Additional notes about the copy
        """
        self.book_id = book_id
        self.barcode = barcode
        self.condition = condition
        self.location = location
        self.notes = notes
        self.is_available = True
    
    def __repr__(self):
        """Return a string representation of the book copy."""
        return f"<BookCopy {self.barcode} (Book ID: {self.book_id})>"
    
    def to_dict(self):
        """Convert the book copy to a dictionary.
        
        Returns:
            dict: Dictionary representation of the book copy
        """
        return {
            'copy_id': self.copy_id,
            'book_id': self.book_id,
            'barcode': self.barcode,
            'is_available': self.is_available,
            'condition': self.condition,
            'location': self.location,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_barcode(cls, barcode):
        """Get a book copy by its barcode.
        
        Args:
            barcode (str): Barcode of the book copy
            
        Returns:
            BookCopy: The book copy if found, None otherwise
        """
        return cls.query.filter_by(barcode=barcode).first()
    
    @classmethod
    def get_available_copies(cls, book_id):
        """Get all available copies of a book.
        
        Args:
            book_id (int): ID of the book
            
        Returns:
            list: List of available book copies
        """
        return cls.query.filter_by(book_id=book_id, is_available=True).all()
    
    @classmethod
    def get_by_condition(cls, condition):
        """Get all book copies with a specific condition.
        
        Args:
            condition (str): Condition to filter by
            
        Returns:
            list: List of book copies with the specified condition
        """
        return cls.query.filter_by(condition=condition).all()
    
    def mark_as_available(self):
        """Mark the book copy as available."""
        self.is_available = True
        self.updated_at = datetime.now(UTC)
    
    def mark_as_unavailable(self):
        """Mark the book copy as unavailable."""
        self.is_available = False
        self.updated_at = datetime.now(UTC)
    
    def update_condition(self, new_condition):
        """Update the condition of the book copy.
        
        Args:
            new_condition (str): New condition of the book copy
            
        Returns:
            bool: True if the condition was updated, False otherwise
        """
        if new_condition not in ['new', 'good', 'fair', 'poor', 'damaged']:
            return False
        
        self.condition = new_condition
        self.updated_at = datetime.now(UTC)
        return True 