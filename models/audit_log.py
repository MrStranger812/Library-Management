"""
AuditLog model for the Library Management System.
Tracks system actions and changes for security and accountability purposes.
"""

from datetime import UTC, datetime, timedelta
from models import db
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship

class AuditLog(db.Model):
    """Model for tracking system actions and changes."""
    __tablename__ = 'audit_logs'

    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(Integer, nullable=True, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC), nullable=False, index=True)

    # Relationships
    user = relationship('User', backref=db.backref('audit_logs', lazy='dynamic'))

    # Table configuration
    __table_args__ = {'extend_existing': True}

    # Common action types
    ACTIONS = {
        'CREATE': 'create',
        'UPDATE': 'update',
        'DELETE': 'delete',
        'LOGIN': 'login',
        'LOGOUT': 'logout',
        'BORROW': 'borrow',
        'RETURN': 'return',
        'RESERVE': 'reserve',
        'CANCEL': 'cancel',
        'PAYMENT': 'payment'
    }

    # Common resource types
    RESOURCE_TYPES = {
        'USER': 'user',
        'BOOK': 'book',
        'BORROWING': 'borrowing',
        'RESERVATION': 'reservation',
        'FINE': 'fine',
        'EVENT': 'event',
        'MEMBERSHIP': 'membership'
    }

    def __init__(self, action, resource_type, user_id=None, resource_id=None, 
                 details=None, ip_address=None, user_agent=None):
        """Initialize a new audit log entry."""
        if action not in self.ACTIONS.values():
            raise ValueError(f"Invalid action. Must be one of: {', '.join(self.ACTIONS.values())}")
        if resource_type not in self.RESOURCE_TYPES.values():
            raise ValueError(f"Invalid resource type. Must be one of: {', '.join(self.RESOURCE_TYPES.values())}")
        
        self.action = action
        self.resource_type = resource_type
        self.user_id = user_id
        self.resource_id = resource_id
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent

    def to_dict(self):
        """Convert audit log to dictionary representation."""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user': {
                'username': self.user.username,
                'full_name': self.user.full_name
            } if self.user else None
        }

    @classmethod
    def log_action(cls, action, resource_type, user_id=None, resource_id=None, 
                   details=None, ip_address=None, user_agent=None):
        """Create a new audit log entry."""
        log = cls(
            action=action,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
        return log

    @classmethod
    def get_by_id(cls, log_id):
        """Get an audit log by its ID."""
        return cls.query.get(log_id)

    @classmethod
    def get_by_resource(cls, resource_type, resource_id):
        """Get all audit logs for a specific resource."""
        return cls.query.filter_by(
            resource_type=resource_type,
            resource_id=resource_id
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_user(cls, user_id):
        """Get all audit logs for a specific user."""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_action(cls, action):
        """Get all audit logs for a specific action."""
        return cls.query.filter_by(action=action).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_date_range(cls, start_date, end_date):
        """Get all audit logs within a date range."""
        return cls.query.filter(
            cls.created_at >= start_date,
            cls.created_at <= end_date
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_recent_logs(cls, limit=100):
        """Get the most recent audit logs."""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_user_activity(cls, user_id, days=30):
        """Get user activity logs for the last N days."""
        start_date = datetime.now(UTC) - timedelta(days=days)
        return cls.query.filter(
            cls.user_id == user_id,
            cls.created_at >= start_date
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_resource_history(cls, resource_type, resource_id, days=30):
        """Get resource history for the last N days."""
        start_date = datetime.now(UTC) - timedelta(days=days)
        return cls.query.filter(
            cls.resource_type == resource_type,
            cls.resource_id == resource_id,
            cls.created_at >= start_date
        ).order_by(cls.created_at.desc()).all()

    def __repr__(self):
        """String representation of the audit log."""
        return f'<AuditLog {self.log_id}: {self.action} on {self.resource_type}>' 