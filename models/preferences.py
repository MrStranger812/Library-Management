from extensions import db
from datetime import datetime

class Preferences(db.Model):
    """Model for storing user preferences."""
    __tablename__ = 'preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    timezone = db.Column(db.String(50), default='UTC')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with User model
    user = db.relationship('User', backref=db.backref('preferences', uselist=False))

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Convert preferences to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'theme': self.theme,
            'language': self.language,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'timezone': self.timezone,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def get_by_user_id(cls, user_id):
        """Get preferences for a specific user."""
        return cls.query.filter_by(user_id=user_id).first()

    def update(self, **kwargs):
        """Update preferences."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self