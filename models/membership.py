"""
Membership model for the Library Management System.
Manages user memberships and membership types.
"""

from datetime import UTC, datetime, timedelta
from models import db

class MembershipType(db.Model):
    """Model for different types of library memberships."""
    __tablename__ = 'membership_types'
    
    membership_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    max_books_allowed = db.Column(db.Integer, nullable=False, default=5)
    loan_duration_days = db.Column(db.Integer, nullable=False, default=14)
    fine_rate_per_day = db.Column(db.Numeric(10, 2), nullable=False, default=0.50)
    annual_fee = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    # Relationships
    memberships = db.relationship('UserMembership', back_populates='membership_type', lazy='dynamic')
    
    def __init__(self, name, description=None, max_books_allowed=5, loan_duration_days=14,
                 fine_rate_per_day=0.50, annual_fee=0.00, is_active=True):
        """Initialize a new membership type."""
        self.name = name
        self.description = description
        self.max_books_allowed = max_books_allowed
        self.loan_duration_days = loan_duration_days
        self.fine_rate_per_day = fine_rate_per_day
        self.annual_fee = annual_fee
        self.is_active = is_active
    
    def to_dict(self):
        """Convert membership type to dictionary representation."""
        return {
            'membership_type_id': self.membership_type_id,
            'name': self.name,
            'description': self.description,
            'max_books_allowed': self.max_books_allowed,
            'loan_duration_days': self.loan_duration_days,
            'fine_rate_per_day': float(self.fine_rate_per_day),
            'annual_fee': float(self.annual_fee),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_id(cls, membership_type_id):
        """Get a membership type by its ID."""
        return cls.query.get(membership_type_id)
    
    @classmethod
    def get_active_types(cls):
        """Get all active membership types."""
        return cls.query.filter_by(is_active=True).order_by(cls.annual_fee).all()
    
    def __repr__(self):
        """String representation of the membership type."""
        return f'<MembershipType {self.name}>'

class UserMembership(db.Model):
    """Model for user memberships."""
    __tablename__ = 'user_memberships'
    
    membership_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    membership_type_id = db.Column(db.Integer, db.ForeignKey('membership_types.membership_type_id', ondelete='RESTRICT'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    # Relationships
    user = db.relationship('User', back_populates='memberships', lazy='joined')
    membership_type = db.relationship('MembershipType', back_populates='memberships', lazy='joined')
    
    def __init__(self, user_id, membership_type_id, start_date=None, end_date=None, duration_months=12):
        """Initialize a new user membership."""
        self.user_id = user_id
        self.membership_type_id = membership_type_id
        self.start_date = start_date or datetime.now(UTC).date()
        if end_date:
            self.end_date = end_date
        else:
            self.end_date = self.start_date + timedelta(days=duration_months * 30)
        self.is_active = True
    
    def to_dict(self):
        """Convert user membership to dictionary representation."""
        return {
            'membership_id': self.membership_id,
            'user_id': self.user_id,
            'membership_type_id': self.membership_type_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'membership_type': self.membership_type.to_dict() if self.membership_type else None,
            'user': {
                'username': self.user.username,
                'full_name': self.user.full_name
            } if self.user else None
        }
    
    @classmethod
    def get_by_id(cls, membership_id):
        """Get a user membership by its ID."""
        return cls.query.get(membership_id)
    
    @classmethod
    def get_user_current_membership(cls, user_id):
        """Get user's current active membership."""
        return cls.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            cls.end_date > datetime.now(UTC).date()
        ).order_by(cls.end_date.desc()).first()
    
    @classmethod
    def get_user_membership_history(cls, user_id):
        """Get user's membership history."""
        return cls.query.filter_by(user_id=user_id).order_by(cls.start_date.desc()).all()
    
    @classmethod
    def get_expiring_memberships(cls, days=30):
        """Get memberships expiring within the specified number of days."""
        expiry_date = datetime.now(UTC).date() + timedelta(days=days)
        return cls.query.filter(
            cls.is_active == True,
            cls.end_date <= expiry_date,
            cls.end_date > datetime.now(UTC).date()
        ).order_by(cls.end_date).all()
    
    def renew(self, duration_months=12):
        """Renew the membership for the specified duration."""
        if not self.is_active:
            raise ValueError("Cannot renew an inactive membership")
        
        self.end_date = self.end_date + timedelta(days=duration_months * 30)
        self.updated_at = datetime.now(UTC)
    
    def deactivate(self):
        """Deactivate the membership."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)
    
    def __repr__(self):
        """String representation of the user membership."""
        return f'<UserMembership {self.membership_id}: User {self.user_id}>'