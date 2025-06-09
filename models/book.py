"""
Book model for the Library Management System.
"""

from models import db
from datetime import UTC, datetime
from models.publisher import Publisher
from models.category import Category
from models.author import Author
from models.book_author import BookAuthor
from models.book_review import BookReview
from models.base_model import BaseModel

class Book(BaseModel):
    """Model for books in the library."""
    __tablename__ = 'books'
    
    book_id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    publication_date = db.Column(db.Date, index=True)
    price = db.Column(db.Numeric(10, 2))
    stock_quantity = db.Column(db.Integer, default=0)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.publisher_id', ondelete='SET NULL'), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'), index=True)

    # Relationships
    publisher = db.relationship('Publisher', backref=db.backref('books', lazy='dynamic'))
    category = db.relationship('Category', backref=db.backref('books', lazy='dynamic'))
    authors = db.relationship('Author', secondary='book_authors', backref=db.backref('books', lazy='dynamic'))
    reviews = db.relationship('BookReview', backref='book', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, isbn, title, description=None, publication_date=None, price=None,
                 stock_quantity=0, publisher_id=None, category_id=None):
        """Initialize a new book."""
        self.isbn = isbn
        self.title = title
        self.description = description
        self.publication_date = publication_date
        self.price = price
        self.stock_quantity = stock_quantity
        self.publisher_id = publisher_id
        self.category_id = category_id
        self.is_active = True

    def to_dict(self, exclude=None, include_relationships=True):
        """Convert book to dictionary."""
        result = super().to_dict(exclude=exclude, include_relationships=include_relationships)
        
        # Add additional book-specific fields
        if self.publication_date:
            result['publication_date'] = self.publication_date.isoformat()
        if self.price:
            result['price'] = float(self.price)
        if include_relationships:
            result['review_count'] = self.reviews.count() if self.reviews else 0
            
        return result

    def __repr__(self):
        """String representation of the book."""
        return f'<Book {self.title}>'