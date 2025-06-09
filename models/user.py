"""
User model for the Library Management System.
Handles user authentication, authorization, and profile management.
"""

from flask_login import UserMixin
from models import db
from extensions import bcrypt
from datetime import UTC, datetime
import re

from models.borrowing import Borrowing

class User(UserMixin, db.Model):
    """Model for library users."""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(100), nullable=False, index=True)
    role = db.Column(db.Enum('admin', 'librarian', 'member'), nullable=False, default='member', index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    last_login = db.Column(db.DateTime, nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    profile_image = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True, index=True)
    address = db.Column(db.Text, nullable=True)

    # Relationships
    borrowings = db.relationship('Borrowing', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('BookReview', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    permissions = db.relationship('UserPermission', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    memberships = db.relationship('UserMembership', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    preferences = db.relationship('UserPreference', backref='user', lazy='joined', cascade='all, delete-orphan')
    managed_branches = db.relationship('LibraryBranch', backref='manager', lazy='dynamic')
    granted_permissions = db.relationship('UserPermission', backref='granted_by_user', lazy='dynamic',
                                        foreign_keys='UserPermission.granted_by')
    reservations = db.relationship('Reservation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, username, password, email, full_name, role='member', phone=None, address=None):
        """Initialize a new user."""
        self.username = username
        self.set_password(password)
        self.email = email
        self.full_name = full_name
        self.role = role
        self.phone = phone
        self.address = address
        self.is_active = True

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verify the user's password."""
        return bcrypt.check_password_hash(self.password, password)

    def get_id(self):
        """Required by Flask-Login."""
        return str(self.user_id)

    @classmethod
    def get_by_id(cls, user_id):
        """Get a user by their ID."""
        return cls.query.get(user_id)

    @classmethod
    def get_by_username(cls, username):
        """Get a user by their username."""
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        """Get a user by their email."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_active_users(cls):
        """Get all active users."""
        return cls.query.filter_by(is_active=True).order_by(cls.username).all()

    @classmethod
    def get_users_by_role(cls, role):
        """Get all users with a specific role."""
        return cls.query.filter_by(role=role, is_active=True).order_by(cls.username).all()

    @classmethod
    def search_users(cls, query):
        """Search users by username, email, or full name."""
        search_term = f"%{query}%"
        return cls.query.filter(
            (cls.username.ilike(search_term)) |
            (cls.email.ilike(search_term)) |
            (cls.full_name.ilike(search_term))
        ).order_by(cls.username).all()

    def has_permission(self, permission_name):
        """Check if the user has a specific permission."""
        return any(p.permission.permission_name == permission_name for p in self.permissions)

    def update_last_login(self):
        """Update the user's last login timestamp."""
        self.last_login = datetime.now(UTC)
        db.session.commit()

    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def activate(self):
        """Activate the user account."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_image': self.profile_image,
            'membership': self.memberships.filter_by(is_active=True).first().to_dict() if self.memberships.filter_by(is_active=True).first() else None
        }

    @staticmethod
    def validate_email(email):
        """Validate email format."""
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        return bool(re.match(pattern, email))

    def __repr__(self):
        """String representation of the user."""
        return f'<User {self.username}>'

    def active_borrowings_count(self):
        """Get count of active borrowings."""
        return self.borrowings.filter_by(status='borrowed').count()

    def get_borrowing_history(self):
        """Get user's borrowing history."""
        return self.borrowings.order_by(Borrowing.borrow_date.desc()).all()

    def total_fines(self):
        """Calculate total fines for the user."""
        from models.fine import Fine
        from sqlalchemy import func
        result = db.session.query(func.sum(Fine.amount)).filter_by(user_id=self.user_id).scalar()
        return float(result) if result else 0.0

    def pending_fines(self):
        """Calculate pending (unpaid) fines."""
        from models.fine import Fine
        from sqlalchemy import func
        result = db.session.query(func.sum(Fine.amount)).filter_by(
            user_id=self.user_id,
            is_paid=False
        ).scalar()
        return float(result) if result else 0.0

class Permission(db.Model):
    """Model for user permissions."""
    __tablename__ = 'permissions'
    
    permission_id = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    user_permissions = db.relationship('UserPermission', backref='permission', lazy='dynamic', cascade='all, delete-orphan')

    def __init__(self, permission_name, description=None):
        """Initialize a new permission."""
        self.permission_name = permission_name
        self.description = description

    def to_dict(self):
        """Convert permission to dictionary."""
        return {
            'permission_id': self.permission_id,
            'permission_name': self.permission_name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        """String representation of the permission."""
        return f'<Permission {self.permission_name}>'

class UserPermission(db.Model):
    """Model for user-permission assignments."""
    __tablename__ = 'user_permissions'
    
    user_permission_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id', ondelete='CASCADE'), nullable=False, index=True)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    granted_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=True, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'permission_id', name='unique_user_permission'),
    )

    def __init__(self, user_id, permission_id, granted_by, expires_at=None):
        """Initialize a new user permission."""
        self.user_id = user_id
        self.permission_id = permission_id
        self.granted_by = granted_by
        self.expires_at = expires_at
        self.is_active = True

    def to_dict(self):
        """Convert user permission to dictionary."""
        return {
            'user_permission_id': self.user_permission_id,
            'user_id': self.user_id,
            'permission_id': self.permission_id,
            'granted_by': self.granted_by,
            'granted_at': self.granted_at.isoformat() if self.granted_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active,
            'permission': self.permission.to_dict() if self.permission else None
        }

    def deactivate(self):
        """Deactivate the permission."""
        self.is_active = False

    def __repr__(self):
        """String representation of the user permission."""
        return f'<UserPermission {self.user_id}:{self.permission_id}>'