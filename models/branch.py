"""
Branch model for the Library Management System.
Handles library branch information and inventory management.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import Index, CheckConstraint

class Branch(db.Model):
    """Model for library branches."""
    __tablename__ = 'library_branches'
    
    branch_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    notes = db.Column(db.Text)

    # Relationships
    manager = db.relationship('User', backref=db.backref('managed_branches', lazy='dynamic'))
    copies = db.relationship('BookCopy', backref='branch', lazy='dynamic', cascade='all, delete-orphan')
    events = db.relationship('LibraryEvent', backref='branch', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('email ~* \'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$\'', name='chk_valid_email'),
        CheckConstraint('phone ~* \'^\\+?[1-9]\\d{1,14}$\'', name='chk_valid_phone'),
        Index('idx_branch_name_address', 'name', 'address', unique=True)
    )

    def __init__(self, name, address, phone, email, manager_id=None, notes=None):
        """Initialize a new branch."""
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.manager_id = manager_id
        self.notes = notes
        self.is_active = True

    @classmethod
    def get_by_id(cls, branch_id):
        """Get a branch by its ID."""
        return cls.query.get(branch_id)

    @classmethod
    def get_active_branches(cls):
        """Get all active branches."""
        return cls.query.filter_by(is_active=True).order_by(cls.name).all()

    @classmethod
    def get_branch_by_name(cls, name):
        """Get a branch by its name."""
        return cls.query.filter_by(name=name, is_active=True).first()

    @classmethod
    def search_branches(cls, search_term):
        """Search branches by name, address, or email."""
        search_pattern = f'%{search_term}%'
        return cls.query.filter(
            db.or_(
                cls.name.ilike(search_pattern),
                cls.address.ilike(search_pattern),
                cls.email.ilike(search_pattern)
            ),
            cls.is_active == True
        ).order_by(cls.name).all()

    def get_inventory(self):
        """Get inventory for this branch."""
        from models.book import Book, BookCopy
        return db.session.query(
            Book,
            db.func.count(BookCopy.copy_id).label('total_copies'),
            db.func.sum(db.case((BookCopy.is_available == True, 1), else_=0)).label('available_copies')
        ).join(BookCopy).filter(
            BookCopy.branch_id == self.branch_id
        ).group_by(Book.book_id).all()

    def get_available_books(self):
        """Get all available books in this branch."""
        from models.book import Book, BookCopy
        return Book.query.join(BookCopy).filter(
            BookCopy.branch_id == self.branch_id,
            BookCopy.is_available == True
        ).distinct().all()

    def get_upcoming_events(self):
        """Get upcoming events at this branch."""
        from models.library_event import LibraryEvent
        return LibraryEvent.query.filter(
            LibraryEvent.branch_id == self.branch_id,
            LibraryEvent.event_date >= datetime.now(UTC).date(),
            LibraryEvent.is_active == True
        ).order_by(LibraryEvent.event_date).all()

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

    def update_manager(self, manager_id):
        """Update the branch manager."""
        self.manager_id = manager_id
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
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'manager': self.manager.to_dict() if self.manager else None
        }

    def __repr__(self):
        """String representation of the branch."""
        return f'<Branch {self.branch_id}: {self.name}>'
