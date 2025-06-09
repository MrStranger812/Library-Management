"""
Author model for the Library Management System.
"""

from models import db
from models.base_model import BaseModel

class Author(BaseModel):
    """Model for book authors."""
    __tablename__ = 'authors'
    
    author_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    biography = db.Column(db.Text)

    def __init__(self, name, biography=None):
        """Initialize a new author."""
        self.name = name
        self.biography = biography
        self.is_active = True

    def __repr__(self):
        """String representation of the author."""
        return f'<Author {self.name}>'
