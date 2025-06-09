"""
Event registration model for the Library Management System.
Tracks user registrations for library events.
"""

from extensions import db
from datetime import UTC, datetime
from models.base_model import BaseModel

class EventRegistration(BaseModel):
    """Model for event registrations."""
    __tablename__ = 'event_registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('library_events.event_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    registration_date = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    status = db.Column(db.Enum('registered', 'attended', 'cancelled', 'no_show'), default='registered', index=True)
    notes = db.Column(db.Text)

    # Relationships
    event = db.relationship('LibraryEvent', back_populates='registrations')
    user = db.relationship('User', back_populates='event_registrations')

    __table_args__ = (
        db.UniqueConstraint('event_id', 'user_id', name='uix_event_user'),
    )

    def __init__(self, event_id, user_id, notes=None):
        """Initialize a new event registration."""
        self.event_id = event_id
        self.user_id = user_id
        self.notes = notes
        self.is_active = True

    @classmethod
    def get_event_registrations(cls, event_id, status=None):
        """Get all registrations for an event, optionally filtered by status."""
        query = cls.query.filter_by(event_id=event_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.registration_date).all()

    @classmethod
    def get_user_registrations(cls, user_id, status=None):
        """Get all registrations for a user, optionally filtered by status."""
        query = cls.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.registration_date.desc()).all()

    def mark_as_attended(self):
        """Mark the registration as attended."""
        self.status = 'attended'
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def mark_as_no_show(self):
        """Mark the registration as no-show."""
        self.status = 'no_show'
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def cancel(self):
        """Cancel the registration."""
        self.status = 'cancelled'
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def to_dict(self, exclude=None, include_relationships=True):
        """Convert registration to dictionary."""
        result = super().to_dict(exclude=exclude, include_relationships=include_relationships)
        
        # Add registration-specific fields
        if self.registration_date:
            result['registration_date'] = self.registration_date.isoformat()
            
        return result

    def __repr__(self):
        """String representation of the registration."""
        return f'<EventRegistration {self.registration_id}: {self.event.title if self.event else "Unknown Event"} - {self.user.username if self.user else "Unknown User"}>' 