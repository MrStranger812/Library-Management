"""
BookReview model for the Library Management System.
Represents user reviews and ratings for books.
"""

from datetime import UTC, datetime
from models import db

class BookReview(db.Model):
    __tablename__ = 'book_reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False, index=True)  # 1-5 stars
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    # Relationships
    book = db.relationship('Book', back_populates='reviews', lazy='joined')
    user = db.relationship('User', back_populates='reviews', lazy='joined')
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        db.UniqueConstraint('book_id', 'user_id', name='unique_book_user_review')
    )
    
    def __init__(self, book_id, user_id, rating, review_text=None):
        """Initialize a new book review."""
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        self.book_id = book_id
        self.user_id = user_id
        self.rating = rating
        self.review_text = review_text
    
    @classmethod
    def get_by_id(cls, review_id):
        """Get a review by its ID."""
        return cls.query.get(review_id)
    
    @classmethod
    def get_book_reviews(cls, book_id):
        """Get all reviews for a book."""
        return cls.query.filter_by(book_id=book_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_user_reviews(cls, user_id):
        """Get all reviews by a user."""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_book_average_rating(cls, book_id):
        """Calculate the average rating for a book."""
        result = cls.query.with_entities(
            db.func.avg(cls.rating).label('average')
        ).filter_by(book_id=book_id).first()
        return float(result.average) if result.average else 0.0
    
    def to_dict(self):
        """Convert review to dictionary representation."""
        return {
            'review_id': self.review_id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'username': self.user.username,
                'full_name': self.user.full_name
            } if self.user else None,
            'book': {
                'title': self.book.title,
                'isbn': self.book.isbn
            } if self.book else None
        }
    
    def __repr__(self):
        """String representation of the review."""
        return f'<BookReview {self.review_id}: {self.rating} stars>' 