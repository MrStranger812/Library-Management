"""
Category model for the Library Management System.
"""

from models import db
from models.base_model import BaseModel

class Category(BaseModel):
    """Model for book categories."""
    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'), index=True)

    # Self-referential relationship for parent-child categories
    parent = db.relationship('Category', remote_side=[category_id], backref=db.backref('subcategories', lazy='dynamic'))

    def __init__(self, name, description=None, parent_category_id=None):
        """Initialize a new category."""
        self.name = name
        self.description = description
        self.parent_category_id = parent_category_id
        self.is_active = True

    def __repr__(self):
        """String representation of the category."""
        return f'<Category {self.name}>'

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