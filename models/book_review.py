from datetime import datetime
from extensions import db

class BookReview(db.Model):
    __tablename__ = 'book_reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    book = db.relationship('Book', back_populates='reviews')
    user = db.relationship('User', back_populates='reviews')
    
    def __init__(self, book_id, user_id, rating, review_text=None):
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        self.book_id = book_id
        self.user_id = user_id
        self.rating = rating
        self.review_text = review_text
    
    def to_dict(self):
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
            } if self.user else None
        }
    
    def __repr__(self):
        return f'<BookReview {self.review_id}: {self.rating} stars>' 