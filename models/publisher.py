"""
Publisher model for the Library Management System.
"""

from models import db
from datetime import UTC, datetime

class Publisher(db.Model):
    """Model for book publishers."""
    __tablename__ = 'publishers'
    
    publisher_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    address = db.Column(db.Text)
    website = db.Column(db.String(255))
    established_year = db.Column(db.Integer, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __init__(self, name, address=None, website=None, established_year=None):
        """Initialize a new publisher."""
        self.name = name
        self.address = address
        self.website = website
        self.established_year = established_year
        self.is_active = True

    def to_dict(self):
        """Convert publisher to dictionary."""
        return {
            'publisher_id': self.publisher_id,
            'name': self.name,
            'address': self.address,
            'website': self.website,
            'established_year': self.established_year,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the publisher."""
        return f'<Publisher {self.name}>' 