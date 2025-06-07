"""
Category model for the Library Management System.
Represents book categories/genres in the library.
"""

from datetime import UTC, datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from models import db

class Category(db.Model):
    """Model representing a book category or genre."""
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}

    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    books = relationship('Book', back_populates='category', lazy='dynamic')

    def __init__(self, name, description=None):
        """Initialize a new category."""
        self.name = name
        self.description = description

    def __repr__(self):
        """Return a string representation of the category."""
        return f"<Category {self.name}>"

    def to_dict(self):
        """Convert the category to a dictionary."""
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book_count': self.books.count() if self.books else 0
        }

    @classmethod
    def get_by_id(cls, category_id):
        """Get a category by its ID."""
        return cls.query.get(category_id)

    @classmethod
    def get_by_name(cls, name):
        """Get a category by its name."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def search_by_name(cls, name):
        """Search categories by name."""
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()

    @classmethod
    def get_all_categories(cls):
        """Get all categories ordered by name."""
        return cls.query.order_by(cls.name).all() 