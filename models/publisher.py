"""
Publisher model for the Library Management System.
Represents publishers of books in the library.
"""

from datetime import UTC, datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from models import db

class Publisher(db.Model):
    """Model representing a book publisher."""
    
    __tablename__ = 'publishers'
    __table_args__ = (
        CheckConstraint(
            "email LIKE '%_@_%.__%'",
            name='valid_email'
        ),
        {'extend_existing': True}
    )
    
    publisher_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    address = Column(String(200))
    phone = Column(String(20))
    email = Column(String(100), unique=True)
    website = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    
    # Relationships
    books = relationship('Book', back_populates='publisher', lazy='dynamic')
    
    def __init__(self, name, address=None, phone=None, email=None, website=None, description=None):
        """Initialize a new publisher.
        
        Args:
            name (str): Name of the publisher
            address (str, optional): Publisher's address
            phone (str, optional): Publisher's phone number
            email (str, optional): Publisher's email address
            website (str, optional): Publisher's website URL
            description (str, optional): Description of the publisher
        """
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.website = website
        self.description = description
    
    def __repr__(self):
        """Return a string representation of the publisher."""
        return f"<Publisher {self.name}>"
    
    def to_dict(self):
        """Convert the publisher to a dictionary.
        
        Returns:
            dict: Dictionary representation of the publisher
        """
        return {
            'publisher_id': self.publisher_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book_count': self.books.count() if self.books else 0
        }
    
    @classmethod
    def get_by_id(cls, publisher_id):
        """Get a publisher by their ID.
        
        Args:
            publisher_id (int): ID of the publisher
            
        Returns:
            Publisher: The publisher if found, None otherwise
        """
        return cls.query.get(publisher_id)
    
    @classmethod
    def get_by_name(cls, name):
        """Get a publisher by their name.
        
        Args:
            name (str): Name of the publisher
            
        Returns:
            Publisher: The publisher if found, None otherwise
        """
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def search_by_name(cls, name):
        """Search publishers by name.
        
        Args:
            name (str): Name to search for
            
        Returns:
            list: List of publishers matching the search
        """
        return cls.query.filter(cls.name.ilike(f'%{name}%')).all()
    
    @classmethod
    def get_all_publishers(cls):
        """Get all publishers ordered by name.
        
        Returns:
            list: List of all publishers
        """
        return cls.query.order_by(cls.name).all() 