from datetime import datetime
from extensions import db

class BookTag(db.Model):
    __tablename__ = 'book_tag_assignments'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('book_tags.tag_id', ondelete='CASCADE'), primary_key=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    book = db.relationship('Book', backref=db.backref('book_tags', lazy='dynamic', cascade='all, delete-orphan'))
    tag = db.relationship('Tag', backref=db.backref('book_tags', lazy='dynamic', cascade='all, delete-orphan'))
    adder = db.relationship('User', backref=db.backref('added_book_tags', lazy='dynamic'))
    
    def __init__(self, book_id, tag_id, added_by=None):
        self.book_id = book_id
        self.tag_id = tag_id
        self.added_by = added_by
    
    def to_dict(self):
        return {
            'book_id': self.book_id,
            'tag_id': self.tag_id,
            'added_by': self.added_by,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }
    
    @classmethod
    def add_tag_to_book(cls, book_id, tag_id, added_by=None):
        """Add a tag to a book if it doesn't already exist."""
        existing = cls.query.filter_by(book_id=book_id, tag_id=tag_id).first()
        if not existing:
            book_tag = cls(book_id=book_id, tag_id=tag_id, added_by=added_by)
            db.session.add(book_tag)
            db.session.commit()
            return book_tag
        return existing
    
    @classmethod
    def remove_tag_from_book(cls, book_id, tag_id):
        """Remove a tag from a book."""
        book_tag = cls.query.filter_by(book_id=book_id, tag_id=tag_id).first()
        if book_tag:
            db.session.delete(book_tag)
            db.session.commit()
            return True
        return False
    
    def __repr__(self):
        return f'<BookTag {self.book_id}:{self.tag_id}>' 