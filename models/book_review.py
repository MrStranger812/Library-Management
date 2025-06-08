"""
BookReview model for the Library Management System.
Represents user reviews for books.
"""

from models import db
from datetime import UTC, datetime

class BookReview(db.Model):
    """Model for book reviews."""
    __tablename__ = 'book_reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __init__(self, book_id, user_id, rating, comment=None):
        """Initialize a new book review."""
        self.book_id = book_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment
        self.is_active = True

    def to_dict(self):
        """Convert review to dictionary."""
        return {
            'review_id': self.review_id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the review."""
        return f'<BookReview {self.review_id}>' 