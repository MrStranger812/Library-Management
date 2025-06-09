"""
Notification and audit models for the Library Management System.
Includes Notification, AuditLog, and UserPreference models.
"""

from models import db
from datetime import UTC, datetime
from models.base_model import BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum('info', 'warning', 'error', 'success'), default='info', index=True)
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='notifications')

    def __init__(self, user_id, title, message, type='info'):
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = type
        self.is_active = True

    @classmethod
    def get_by_id(cls, notification_id):
        """Get a notification by its ID."""
        return cls.query.get(notification_id)

    @classmethod
    def get_user_notifications(cls, user_id, unread_only=False):
        """Get all notifications for a user, optionally filtered to unread only."""
        query = cls.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(cls.created_at.desc()).all()

    def mark_as_read(self):
        """Mark the notification as read."""
        self.is_read = True
        self.read_at = datetime.now(UTC)
        db.session.commit()

    def to_dict(self):
        """Convert notification to dictionary representation."""
        return {
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

class AuditLog(BaseModel):
    __tablename__ = 'audit_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    table_name = db.Column(db.String(50), nullable=False, index=True)
    record_id = db.Column(db.Integer, nullable=False, index=True)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))

    # Relationships
    user = db.relationship('User', backref='audit_logs')

    def __init__(self, action, table_name, record_id, user_id=None, old_values=None, 
                 new_values=None, ip_address=None, user_agent=None):
        self.action = action
        self.table_name = table_name
        self.record_id = record_id
        self.user_id = user_id
        self.old_values = old_values
        self.new_values = new_values
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.is_active = True

    @classmethod
    def get_by_id(cls, log_id):
        """Get an audit log by its ID."""
        return cls.query.get(log_id)

    @classmethod
    def get_table_logs(cls, table_name, record_id=None):
        """Get all audit logs for a table, optionally filtered by record ID."""
        query = cls.query.filter_by(table_name=table_name)
        if record_id:
            query = query.filter_by(record_id=record_id)
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_user_logs(cls, user_id):
        """Get all audit logs for a user."""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

    def to_dict(self):
        """Convert audit log to dictionary representation."""
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'action': self.action,
            'table_name': self.table_name,
            'record_id': self.record_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserPreference(BaseModel):
    __tablename__ = 'user_preferences'
    
    preference_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    preference_key = db.Column(db.String(50), nullable=False, index=True)
    preference_value = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', backref='preferences')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'preference_key', name='unique_user_preference'),
    )

    def __init__(self, user_id, preference_key, preference_value):
        self.user_id = user_id
        self.preference_key = preference_key
        self.preference_value = preference_value
        self.is_active = True

    @classmethod
    def get_by_id(cls, preference_id):
        """Get a preference by its ID."""
        return cls.query.get(preference_id)

    @classmethod
    def get_user_preferences(cls, user_id):
        """Get all preferences for a user as a dictionary."""
        preferences = cls.query.filter_by(user_id=user_id).all()
        return {p.preference_key: p.preference_value for p in preferences}

    @classmethod
    def get_preference(cls, user_id, preference_key):
        """Get a specific preference for a user."""
        return cls.query.filter_by(
            user_id=user_id,
            preference_key=preference_key
        ).first()

    def update_value(self, value):
        """Update the preference value."""
        self.preference_value = value
        db.session.commit()

    def to_dict(self):
        """Convert preference to dictionary representation."""
        return {
            'preference_id': self.preference_id,
            'user_id': self.user_id,
            'preference_key': self.preference_key,
            'preference_value': self.preference_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }