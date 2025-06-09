"""
Category model for the Library Management System.
"""

from models import db
from datetime import UTC, datetime

class Category(db.Model):
    """Model for book categories."""
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Self-referential relationship for parent-child categories
    parent = db.relationship('Category', remote_side=[category_id], backref=db.backref('subcategories', lazy='dynamic'))

    def __init__(self, name, description=None, parent_category_id=None):
        """Initialize a new category."""
        self.name = name
        self.description = description
        self.parent_category_id = parent_category_id
        self.is_active = True

    def to_dict(self):
        """Convert category to dictionary."""
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'parent_category_id': self.parent_category_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the category."""
        return f'<Category {self.name}>'

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