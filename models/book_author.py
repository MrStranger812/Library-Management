"""
Book author model for the Library Management System.
Tracks the relationship between books and authors.
"""

from extensions import db
from datetime import UTC, datetime

class BookAuthor(db.Model):
    """Model for book-author relationships."""
    __tablename__ = 'book_authors'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id', ondelete='CASCADE'), primary_key=True, index=True)
    role = db.Column(db.Enum('author', 'co-author', 'editor', 'translator'), default='author')
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)

    # Relationships
    book = db.relationship('Book', back_populates='authors')
    author = db.relationship('Author', back_populates='books')

    def __init__(self, book_id, author_id, role='author'):
        """Initialize a new book-author relationship."""
        self.book_id = book_id
        self.author_id = author_id
        self.role = role

    @classmethod
    def get_book_authors(cls, book_id):
        """Get all authors for a book."""
        return cls.query.filter_by(book_id=book_id).all()

    @classmethod
    def get_author_books(cls, author_id):
        """Get all books by an author."""
        return cls.query.filter_by(author_id=author_id).all()

    def to_dict(self):
        """Convert book-author relationship to dictionary."""
        return {
            'book_id': self.book_id,
            'author_id': self.author_id,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'book': self.book.to_dict() if self.book else None,
            'author': self.author.to_dict() if self.author else None
        }

    def __repr__(self):
        """String representation of the book-author relationship."""
        return f'<BookAuthor {self.book.title if self.book else "Unknown Book"} - {self.author.full_name if self.author else "Unknown Author"}>' 