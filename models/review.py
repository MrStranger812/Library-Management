"""
Review model for the Library Management System.
Handles book reviews and ratings.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import Index, CheckConstraint, and_
from sqlalchemy.orm import relationship
from models.base_model import BaseModel

class Review(BaseModel):
    """Model representing a book review in the library system."""
    
    __tablename__ = 'reviews'
    
    # Columns
    review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)

    # Indexes
    __table_args__ = (
        Index('idx_review_user', 'user_id'),
        Index('idx_review_book', 'book_id'),
        Index('idx_review_rating', 'rating'),
        Index('idx_review_created', 'created_at'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='valid_rating_range'),
    )
    
    # Relationships
    user = relationship('User', backref=db.backref('reviews', lazy='dynamic'))
    book = relationship('Book', backref=db.backref('reviews', lazy='dynamic'))
    
    def __init__(self, user_id, book_id, rating, comment=None):
        """
        Initialize a new review.
        
        Args:
            user_id (int): ID of the user writing the review
            book_id (int): ID of the book being reviewed
            rating (int): Rating value (1-5)
            comment (str, optional): Review comment
        """
        self.user_id = user_id
        self.book_id = book_id
        self.rating = rating
        self.comment = comment
        self.is_active = True
    
    @classmethod
    def add_review(cls, user_id, book_id, rating, comment):
        """
        Add or update a book review.
        
        Args:
            user_id (int): ID of the user writing the review
            book_id (int): ID of the book being reviewed
            rating (int): Rating value (1-5)
            comment (str): Review comment
            
        Returns:
            tuple: (success (bool), message (str))
        """
        from models.borrowing import Borrowing
        
        # Check if user has borrowed this book
        has_borrowed = Borrowing.query.filter_by(
            user_id=user_id,
            book_id=book_id
        ).first()
        
        if not has_borrowed:
            return False, "You can only review books you have borrowed"
        
        # Check if user already reviewed this book
        existing_review = cls.query.filter_by(
            user_id=user_id,
            book_id=book_id
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.updated_at = datetime.now(UTC)
            message = "Review updated successfully"
        else:
            # Create new review
            review = cls(user_id=user_id, book_id=book_id, rating=rating, comment=comment)
            db.session.add(review)
            message = "Review added successfully"
        
        try:
            db.session.commit()
            return True, message
        except Exception as e:
            db.session.rollback()
            return False, f"Error saving review: {str(e)}"
    
    @classmethod
    def get_book_reviews(cls, book_id, limit=None, offset=None):
        """
        Get all reviews for a specific book.
        
        Args:
            book_id (int): ID of the book
            limit (int, optional): Maximum number of reviews to return
            offset (int, optional): Number of reviews to skip
            
        Returns:
            list: List of Review objects
        """
        query = cls.query.filter_by(book_id=book_id).order_by(cls.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    @classmethod
    def get_user_reviews(cls, user_id, limit=None, offset=None):
        """
        Get all reviews by a specific user.
        
        Args:
            user_id (int): ID of the user
            limit (int, optional): Maximum number of reviews to return
            offset (int, optional): Number of reviews to skip
            
        Returns:
            list: List of Review objects
        """
        query = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc())
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
            
        return query.all()
    
    @classmethod
    def get_average_rating(cls, book_id):
        """
        Get the average rating for a book.
        
        Args:
            book_id (int): ID of the book
            
        Returns:
            float: Average rating
        """
        from sqlalchemy import func
        result = db.session.query(func.avg(cls.rating)).filter_by(book_id=book_id).scalar()
        return round(result, 2) if result else 0
    
    def __repr__(self):
        """String representation of the review."""
        return f"<Review {self.review_id}: {self.user_id} -> {self.book_id} ({self.rating} stars)>"