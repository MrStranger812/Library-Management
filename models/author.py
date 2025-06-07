"""
Author model for the Library Management System.
Represents authors of books in the library.
"""

from datetime import UTC, datetime
from models import db

class Author(db.Model):
    __tablename__ = 'authors'
    __table_args__ = {'extend_existing': True}
    
    author_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False, index=True)
    last_name = db.Column(db.String(50), nullable=False, index=True)
    biography = db.Column(db.Text)
    birth_date = db.Column(db.Date, index=True)
    death_date = db.Column(db.Date, index=True)
    nationality = db.Column(db.String(50), index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    # Relationships
    books = db.relationship('Book', secondary='book_authors', back_populates='authors', lazy='dynamic')
    
    def __init__(self, first_name, last_name, biography=None, birth_date=None, death_date=None, nationality=None):
        """Initialize a new Author instance."""
        self.first_name = first_name
        self.last_name = last_name
        self.biography = biography
        self.birth_date = birth_date
        self.death_date = death_date
        self.nationality = nationality
    
    @classmethod
    def get_by_id(cls, author_id):
        """Get an author by their ID."""
        return cls.query.get(author_id)
    
    @classmethod
    def get_by_name(cls, first_name, last_name):
        """Get an author by their first and last name."""
        return cls.query.filter_by(first_name=first_name, last_name=last_name).first()
    
    @classmethod
    def search_by_name(cls, name):
        """Search authors by name (first or last)."""
        return cls.query.filter(
            (cls.first_name.ilike(f'%{name}%')) | 
            (cls.last_name.ilike(f'%{name}%'))
        ).all()
    
    @classmethod
    def get_all_authors(cls):
        """Get all authors ordered by last name."""
        return cls.query.order_by(cls.last_name, cls.first_name).all()
    
    def get_full_name(self):
        """Get the author's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert author to dictionary representation."""
        return {
            'author_id': self.author_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'biography': self.biography,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'death_date': self.death_date.isoformat() if self.death_date else None,
            'nationality': self.nationality,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book_count': self.books.count() if self.books else 0
        }
    
    def __repr__(self):
        """String representation of the author."""
        return f'<Author {self.get_full_name()}>'
