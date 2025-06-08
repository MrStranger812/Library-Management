"""
Tag models for the Library Management System.
Includes Tag and BookTag models for categorizing books with tags.
"""

from extensions import db
from datetime import UTC, datetime

class Tag(db.Model):
    """Model for book tags."""
    __tablename__ = 'tags'
    
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(200))
    color = db.Column(db.String(7), default='#6c757d')
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    books = db.relationship('BookTag', back_populates='tag', lazy='dynamic')
    creator = db.relationship('User', back_populates='created_tags')

    def __init__(self, name, description=None, color='#6c757d', created_by=None):
        """Initialize a new tag."""
        self.name = name
        self.description = description
        self.color = color
        self.created_by = created_by

    @classmethod
    def get_by_name(cls, name):
        """Get a tag by its name."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_all_tags(cls):
        """Get all tags."""
        return cls.query.order_by(cls.name).all()

    def to_dict(self):
        """Convert tag to dictionary."""
        return {
            'tag_id': self.tag_id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the tag."""
        return f'<Tag {self.name}>'

class BookTag(db.Model):
    """Model for book-tag associations."""
    __tablename__ = 'book_tags'
    
    book_tag_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id', ondelete='CASCADE'), nullable=False, index=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    added_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)

    # Relationships
    book = db.relationship('Book', back_populates='tags')
    tag = db.relationship('Tag', back_populates='books')
    adder = db.relationship('User', back_populates='added_book_tags')

    __table_args__ = (
        db.UniqueConstraint('book_id', 'tag_id', name='uix_book_tag'),
    )

    def __init__(self, book_id, tag_id, added_by=None):
        """Initialize a new book-tag association."""
        self.book_id = book_id
        self.tag_id = tag_id
        self.added_by = added_by

    @classmethod
    def get_book_tags(cls, book_id):
        """Get all tags for a book."""
        return cls.query.filter_by(book_id=book_id).all()

    @classmethod
    def get_tagged_books(cls, tag_id):
        """Get all books with a specific tag."""
        return cls.query.filter_by(tag_id=tag_id).all()

    def to_dict(self):
        """Convert book-tag association to dictionary."""
        return {
            'book_tag_id': self.book_tag_id,
            'book_id': self.book_id,
            'tag_id': self.tag_id,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None,
            'book': self.book.to_dict() if self.book else None,
            'tag': self.tag.to_dict() if self.tag else None,
            'adder': self.adder.to_dict() if self.adder else None
        }

    def __repr__(self):
        """String representation of the book-tag association."""
        return f'<BookTag {self.book.title if self.book else "Unknown Book"} - {self.tag.name if self.tag else "Unknown Tag"}>' 