"""
Publisher model for the Library Management System.
"""

from models import db
from models.base_model import BaseModel

class Publisher(BaseModel):
    """Model for book publishers."""
    __tablename__ = 'publishers'
    
    publisher_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    address = db.Column(db.Text)
    website = db.Column(db.String(255))
    established_year = db.Column(db.Integer, index=True)

    def __init__(self, name, address=None, website=None, established_year=None):
        """Initialize a new publisher."""
        self.name = name
        self.address = address
        self.website = website
        self.established_year = established_year
        self.is_active = True

    def __repr__(self):
        """String representation of the publisher."""
        return f'<Publisher {self.name}>' 