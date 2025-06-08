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

class Book(db.Model):
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
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = db.Column(db.Boolean, default=True, index=True)

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

    def to_dict(self):
        """Convert book to dictionary."""
        return {
            'book_id': self.book_id,
            'isbn': self.isbn,
            'title': self.title,
            'description': self.description,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'price': float(self.price) if self.price else None,
            'stock_quantity': self.stock_quantity,
            'publisher_id': self.publisher_id,
            'category_id': self.category_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'authors': [author.to_dict() for author in self.authors],
            'publisher': self.publisher.to_dict() if self.publisher else None,
            'category': self.category.to_dict() if self.category else None,
            'review_count': self.reviews.count() if self.reviews else 0
        }

    def __repr__(self):
        """String representation of the book."""
        return f'<Book {self.title}>'