"""
Book copy model for the Library Management System.
Tracks individual copies of books in the library.
"""

from extensions import db
from datetime import UTC, datetime
from models.base_model import BaseModel

class BookCopy(BaseModel):
    """Model for individual book copies."""
    __tablename__ = 'book_copies'
    
    copy_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('library_branches.branch_id', ondelete='CASCADE'), nullable=False, index=True)
    barcode = db.Column(db.String(50), unique=True, index=True)
    acquisition_date = db.Column(db.Date, default=datetime.now(UTC).date, nullable=False)
    condition = db.Column(db.Enum('excellent', 'good', 'fair', 'poor', 'damaged'), default='good')
    location = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2))
    is_available = db.Column(db.Boolean, default=True, index=True)
    notes = db.Column(db.Text)

    # Relationships
    book = db.relationship('Book', back_populates='copies')
    branch = db.relationship('LibraryBranch', back_populates='book_copies')
    borrowings = db.relationship('Borrowing', back_populates='book_copy', lazy='dynamic')

    def __init__(self, book_id, branch_id, barcode=None, condition='good', location=None, price=None, notes=None):
        """Initialize a new book copy."""
        self.book_id = book_id
        self.branch_id = branch_id
        self.barcode = barcode
        self.condition = condition
        self.location = location
        self.price = price
        self.notes = notes
        self.is_available = True

    @classmethod
    def get_by_barcode(cls, barcode):
        """Get a book copy by its barcode."""
        return cls.query.filter_by(barcode=barcode).first()

    @classmethod
    def get_available_copies(cls, book_id):
        """Get all available copies of a book."""
        return cls.query.filter_by(book_id=book_id, is_available=True).all()

    @classmethod
    def get_branch_copies(cls, branch_id):
        """Get all copies in a branch."""
        return cls.query.filter_by(branch_id=branch_id).all()

    def mark_as_borrowed(self):
        """Mark the copy as borrowed."""
        self.is_available = False
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def mark_as_available(self):
        """Mark the copy as available."""
        self.is_available = True
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def update_condition(self, new_condition):
        """Update the condition of the copy."""
        if new_condition not in ['excellent', 'good', 'fair', 'poor', 'damaged']:
            raise ValueError("Invalid condition value")
        self.condition = new_condition
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def to_dict(self, exclude=None, include_relationships=True):
        """Convert book copy to dictionary."""
        result = super().to_dict(exclude=exclude, include_relationships=include_relationships)
        
        # Add book copy specific fields
        if self.acquisition_date:
            result['acquisition_date'] = self.acquisition_date.isoformat()
        if self.price:
            result['price'] = float(self.price)
            
        return result

    def __repr__(self):
        """String representation of the book copy."""
        return f'<BookCopy {self.copy_id}: {self.book.title if self.book else "Unknown Book"} - {self.barcode}>' 