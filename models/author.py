"""
Author model for the Library Management System.
"""

from models import db
from datetime import UTC, datetime

class Author(db.Model):
    """Model for book authors."""
    __tablename__ = 'authors'
    
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    biography = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __init__(self, name, biography=None):
        """Initialize a new author."""
        self.name = name
        self.biography = biography
        self.is_active = True

    def to_dict(self):
        """Convert author to dictionary."""
        return {
            'author_id': self.author_id,
            'name': self.name,
            'biography': self.biography,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the author."""
        return f'<Author {self.name}>'
