from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import db

class AuditLog(db.Model):
    """Model for tracking system actions and changes."""
    __tablename__ = 'audit_logs'

    log_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', backref='audit_logs')

    def __init__(self, action, resource_type, user_id=None, resource_id=None, 
                 details=None, ip_address=None, user_agent=None):
        self.action = action
        self.resource_type = resource_type
        self.user_id = user_id
        self.resource_id = resource_id
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent

    def to_dict(self):
        """Convert audit log to dictionary."""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
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