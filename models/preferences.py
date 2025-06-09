from extensions import db
from datetime import datetime, UTC
from models.base_model import BaseModel

class Preferences(BaseModel):
    """Model for storing user preferences."""
    __tablename__ = 'preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    theme = db.Column(db.String(20), default='light')
    language = db.Column(db.String(10), default='en')
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    timezone = db.Column(db.String(50), default='UTC')

    # Relationship with User model
    user = db.relationship('User', backref=db.backref('preferences', uselist=False))

    def __init__(self, user_id, **kwargs):
        self.user_id = user_id
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.is_active = True

    @classmethod
    def get_by_user_id(cls, user_id):
        """Get preferences for a specific user."""
        return cls.query.filter_by(user_id=user_id).first()

    def update(self, **kwargs):
        """Update preferences."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(UTC)
        db.session.commit()
        return self