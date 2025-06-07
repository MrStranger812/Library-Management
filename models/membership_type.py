"""
MembershipType model for the Library Management System.
Represents types of library memberships.
"""

from models import db

class MembershipType(db.Model):
    __tablename__ = 'membership_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    max_books = db.Column(db.Integer, nullable=False, default=3)
    max_days = db.Column(db.Integer, nullable=False, default=14)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __init__(self, name, description=None, max_books=3, max_days=14, price=0.0, is_active=True):
        self.name = name
        self.description = description
        self.max_books = max_books
        self.max_days = max_days
        self.price = price
        self.is_active = is_active

    @classmethod
    def get_by_id(cls, id):
        """Get a membership type by its ID."""
        return cls.query.get(id)

    @classmethod
    def get_by_name(cls, name):
        """Get a membership type by its name."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_active_types(cls):
        """Get all active membership types."""
        return cls.query.filter_by(is_active=True).all()

    def to_dict(self):
        """Convert membership type to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_books': self.max_books,
            'max_days': self.max_days,
            'price': float(self.price),
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<MembershipType {self.name}>' 