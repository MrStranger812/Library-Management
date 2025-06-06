from extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum('info', 'warning', 'error', 'success'), default='info')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='notifications')

    def __init__(self, user_id, title, message, type='info'):
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = type

    @classmethod
    def get_user_notifications(cls, user_id, unread_only=False):
        query = cls.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(cls.created_at.desc()).all()

    def mark_as_read(self):
        self.is_read = True
        self.read_at = datetime.utcnow()
        db.session.commit()

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    action = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_values = db.Column(db.JSON)
    new_values = db.Column(db.JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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

    @classmethod
    def get_table_logs(cls, table_name, record_id=None):
        query = cls.query.filter_by(table_name=table_name)
        if record_id:
            query = query.filter_by(record_id=record_id)
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_user_logs(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    preference_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    preference_key = db.Column(db.String(50), nullable=False)
    preference_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='preferences')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'preference_key', name='unique_user_preference'),
    )

    def __init__(self, user_id, preference_key, preference_value):
        self.user_id = user_id
        self.preference_key = preference_key
        self.preference_value = preference_value

    @classmethod
    def get_user_preferences(cls, user_id):
        preferences = cls.query.filter_by(user_id=user_id).all()
        return {p.preference_key: p.preference_value for p in preferences}

    @classmethod
    def get_preference(cls, user_id, preference_key):
        return cls.query.filter_by(
            user_id=user_id,
            preference_key=preference_key
        ).first()

    def update_value(self, value):
        self.preference_value = value
        db.session.commit()