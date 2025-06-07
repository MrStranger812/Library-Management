"""
BookAuthor model for the Library Management System.
Represents the many-to-many relationship between books and authors.
"""

from datetime import UTC, datetime
from models import db

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id', ondelete='CASCADE'), primary_key=True, index=True)
    role = db.Column(db.String(20), default='author', index=True)  # author, co-author, editor, translator
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    # Relationships
    book = db.relationship('Book', back_populates='book_authors')
    author = db.relationship('Author', back_populates='book_authors')
    
    def __init__(self, book_id, author_id, role='author'):
        """Initialize a new BookAuthor instance."""
        self.book_id = book_id
        self.author_id = author_id
        self.role = role
    
    @classmethod
    def get_by_ids(cls, book_id, author_id):
        """Get a book-author relationship by book and author IDs."""
        return cls.query.filter_by(book_id=book_id, author_id=author_id).first()
    
    @classmethod
    def get_book_authors(cls, book_id):
        """Get all authors for a book."""
        return cls.query.filter_by(book_id=book_id).all()
    
    @classmethod
    def get_author_books(cls, author_id):
        """Get all books for an author."""
        return cls.query.filter_by(author_id=author_id).all()
    
    @classmethod
    def get_by_role(cls, role):
        """Get all book-author relationships with a specific role."""
        return cls.query.filter_by(role=role).all()
    
    def to_dict(self):
        """Convert book-author relationship to dictionary representation."""
        return {
            'book_id': self.book_id,
            'author_id': self.author_id,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book': self.book.to_dict() if self.book else None,
            'author': self.author.to_dict() if self.author else None
        }
    
    def __repr__(self):
        """String representation of the book-author relationship."""
        return f'<BookAuthor {self.book_id} - {self.author_id} ({self.role})>' 