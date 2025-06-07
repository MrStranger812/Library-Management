"""
BookTag model for the Library Management System.
Provides functionality for managing the many-to-many relationship between books and tags.
"""

from models import db
from datetime import UTC, datetime

class BookTag(db.Model):
    __tablename__ = 'book_tags'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True, index=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id', ondelete='CASCADE'), primary_key=True, index=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    added_at = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    
    # Relationships
    book = db.relationship('Book', backref=db.backref('book_tags', lazy='dynamic', cascade='all, delete-orphan'))
    tag = db.relationship('Tag', backref=db.backref('book_tags', lazy='dynamic', cascade='all, delete-orphan'))
    adder = db.relationship('User', backref=db.backref('added_book_tags', lazy='dynamic'))
    
    def __init__(self, book_id, tag_id, added_by=None):
        self.book_id = book_id
        self.tag_id = tag_id
        self.added_by = added_by
    
    @classmethod
    def get_by_ids(cls, book_id, tag_id):
        """Get a book tag by book ID and tag ID."""
        return cls.query.filter_by(book_id=book_id, tag_id=tag_id).first()
    
    @classmethod
    def get_book_tags(cls, book_id):
        """Get all tags for a book."""
        return cls.query.filter_by(book_id=book_id).all()
    
    @classmethod
    def get_tagged_books(cls, tag_id):
        """Get all books with a specific tag."""
        return cls.query.filter_by(tag_id=tag_id).all()
    
    @classmethod
    def add_tag_to_book(cls, book_id, tag_id, added_by=None):
        """Add a tag to a book if it doesn't already exist."""
        existing = cls.get_by_ids(book_id, tag_id)
        if not existing:
            book_tag = cls(book_id=book_id, tag_id=tag_id, added_by=added_by)
            db.session.add(book_tag)
            db.session.commit()
            return book_tag
        return existing
    
    @classmethod
    def remove_tag_from_book(cls, book_id, tag_id):
        """Remove a tag from a book."""
        book_tag = cls.get_by_ids(book_id, tag_id)
        if book_tag:
            db.session.delete(book_tag)
            db.session.commit()
            return True
        return False
    
    def to_dict(self):
        """Convert book tag to dictionary representation."""
        return {
            'book_id': self.book_id,
            'tag_id': self.tag_id,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }
    
    def __repr__(self):
        return f'<BookTag {self.book_id}:{self.tag_id}>' 