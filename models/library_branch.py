"""
Library branch model for the Library Management System.
Tracks different branches of the library.
"""

from extensions import db
from datetime import UTC, datetime

class LibraryBranch(db.Model):
    """Model for library branches."""
    __tablename__ = 'library_branches'
    
    branch_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    manager = db.relationship('User', back_populates='managed_branches')
    events = db.relationship('LibraryEvent', back_populates='branch', lazy='dynamic')
    book_copies = db.relationship('BookCopy', back_populates='branch', lazy='dynamic')

    def __init__(self, name, address, phone=None, email=None, manager_id=None):
        """Initialize a new library branch."""
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.manager_id = manager_id
        self.is_active = True

    @classmethod
    def get_by_id(cls, branch_id):
        """Get a branch by its ID."""
        return cls.query.get(branch_id)

    @classmethod
    def get_active_branches(cls):
        """Get all active branches."""
        return cls.query.filter_by(is_active=True).all()

    def deactivate(self):
        """Deactivate the branch."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def activate(self):
        """Activate the branch."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def update_details(self, **kwargs):
        """Update branch details."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def to_dict(self):
        """Convert branch to dictionary."""
        return {
            'branch_id': self.branch_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'manager': self.manager.to_dict() if self.manager else None,
            'event_count': self.events.count() if self.events else 0,
            'book_copy_count': self.book_copies.count() if self.book_copies else 0
        }

    def __repr__(self):
        """String representation of the branch."""
        return f'<LibraryBranch {self.branch_id}: {self.name}>' 