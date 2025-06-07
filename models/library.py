"""
Library models for the Library Management System.
Includes LibraryBranch, MembershipType, UserMembership, LibraryEvent, and EventRegistration models.
"""

from models import db
from datetime import UTC, datetime

class LibraryBranch(db.Model):
    """Model for library branches."""
    __tablename__ = 'library_branches'
    
    branch_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), index=True)
    email = db.Column(db.String(100), index=True)
    opening_hours = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    manager = db.relationship('User', backref='managed_branches', lazy='joined')
    book_copies = db.relationship('BookCopy', backref='branch', lazy='dynamic', cascade='all, delete-orphan')
    events = db.relationship('LibraryEvent', backref='branch', lazy='dynamic', cascade='all, delete-orphan')
    borrowings = db.relationship('Borrowing', backref='branch', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, name, address, phone=None, email=None, opening_hours=None, manager_id=None):
        """Initialize a new library branch."""
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.opening_hours = opening_hours
        self.manager_id = manager_id
        self.is_active = True

    def to_dict(self):
        """Convert library branch to dictionary representation."""
        return {
            'branch_id': self.branch_id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'opening_hours': self.opening_hours,
            'manager_id': self.manager_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'manager': {
                'username': self.manager.username,
                'full_name': self.manager.full_name
            } if self.manager else None,
            'book_count': self.book_copies.count(),
            'event_count': self.events.count()
        }

    @classmethod
    def get_by_id(cls, branch_id):
        """Get a library branch by its ID."""
        return cls.query.get(branch_id)

    @classmethod
    def get_by_name(cls, name):
        """Get a library branch by its name."""
        return cls.query.filter_by(name=name).first()

    @classmethod
    def get_active_branches(cls):
        """Get all active library branches."""
        return cls.query.filter_by(is_active=True).order_by(cls.name).all()

    @classmethod
    def get_all_branches(cls):
        """Get all library branches."""
        return cls.query.order_by(cls.name).all()

    @classmethod
    def search_branches(cls, query):
        """Search branches by name, address, or email."""
        search_term = f"%{query}%"
        return cls.query.filter(
            (cls.name.ilike(search_term)) |
            (cls.address.ilike(search_term)) |
            (cls.email.ilike(search_term))
        ).order_by(cls.name).all()

    def deactivate(self):
        """Deactivate the library branch."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self):
        """Activate the library branch."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def __repr__(self):
        """String representation of the library branch."""
        return f'<LibraryBranch {self.name}>'

class MembershipType(db.Model):
    __tablename__ = 'membership_types'
    
    type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    max_books = db.Column(db.Integer, nullable=False, default=5)
    loan_period = db.Column(db.Integer, nullable=False, default=14)  # in days
    renewal_period = db.Column(db.Integer, nullable=False, default=365)  # in days
    fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    memberships = db.relationship('UserMembership', backref='membership_type', lazy=True, cascade='all, delete-orphan')

    def __init__(self, name, description=None, max_books=5, loan_period=14, renewal_period=365, fee=0):
        self.name = name
        self.description = description
        self.max_books = max_books
        self.loan_period = loan_period
        self.renewal_period = renewal_period
        self.fee = fee

    @classmethod
    def get_by_id(cls, type_id):
        """Get a membership type by its ID."""
        return cls.query.get(type_id)

    @classmethod
    def get_all_types(cls):
        """Get all membership types."""
        return cls.query.all()

class UserMembership(db.Model):
    __tablename__ = 'user_memberships'
    
    membership_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = db.Column(db.Integer, db.ForeignKey('membership_types.type_id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.Enum('active', 'expired', 'suspended', 'cancelled'), default='active', index=True)
    payment_status = db.Column(db.Enum('paid', 'pending', 'overdue'), default='pending', index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='memberships')

    def __init__(self, user_id, type_id, end_date):
        self.user_id = user_id
        self.type_id = type_id
        self.end_date = end_date

    @classmethod
    def get_by_id(cls, membership_id):
        """Get a membership by its ID."""
        return cls.query.get(membership_id)

    @classmethod
    def get_active_membership(cls, user_id):
        """Get the active membership for a user."""
        return cls.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

    def renew(self, renewal_period):
        """Renew the membership for the specified period."""
        self.end_date = datetime.utcnow() + renewal_period
        self.status = 'active'
        db.session.commit()

    def suspend(self):
        """Suspend the membership."""
        self.status = 'suspended'
        db.session.commit()

    def cancel(self):
        """Cancel the membership."""
        self.status = 'cancelled'
        db.session.commit()

class LibraryEvent(db.Model):
    __tablename__ = 'library_events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('library_branches.branch_id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False, index=True)
    duration = db.Column(db.Integer)  # in minutes
    capacity = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy=True, cascade='all, delete-orphan')

    def __init__(self, branch_id, title, event_date, description=None, duration=None, 
                 capacity=None, registration_required=False):
        self.branch_id = branch_id
        self.title = title
        self.event_date = event_date
        self.description = description
        self.duration = duration
        self.capacity = capacity
        self.registration_required = registration_required

    @classmethod
    def get_by_id(cls, event_id):
        """Get an event by its ID."""
        return cls.query.get(event_id)

    @classmethod
    def get_upcoming_events(cls):
        """Get all upcoming events."""
        return cls.query.filter(cls.event_date > datetime.utcnow()).all()

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('library_events.event_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = db.Column(db.Enum('registered', 'attended', 'cancelled', 'no_show'), default='registered', index=True)
    notes = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', backref='event_registrations')

    def __init__(self, event_id, user_id):
        self.event_id = event_id
        self.user_id = user_id

    @classmethod
    def get_by_id(cls, registration_id):
        """Get a registration by its ID."""
        return cls.query.get(registration_id)

    @classmethod
    def get_event_registrations(cls, event_id):
        """Get all registrations for an event."""
        return cls.query.filter_by(event_id=event_id).all()

    def mark_attended(self):
        """Mark the registration as attended."""
        self.status = 'attended'
        db.session.commit()

    def cancel(self):
        """Cancel the registration."""
        self.status = 'cancelled'
        db.session.commit() 