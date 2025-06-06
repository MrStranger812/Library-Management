from datetime import datetime
from extensions import db

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id', ondelete='CASCADE'), primary_key=True)
    role = db.Column(db.String(20), default='author')  # author, co-author, editor, translator
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    book = db.relationship('Book', back_populates='book_authors')
    author = db.relationship('Author', back_populates='book_authors')
    
    def __init__(self, book_id, author_id, role='author'):
        self.book_id = book_id
        self.author_id = author_id
        self.role = role
    
    def to_dict(self):
        return {
            'book_id': self.book_id,
            'author_id': self.author_id,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BookAuthor {self.book_id} - {self.author_id} ({self.role})>' 