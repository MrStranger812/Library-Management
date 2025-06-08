"""
Event registration model for the Library Management System.
Tracks user registrations for library events.
"""

from extensions import db
from datetime import UTC, datetime

class EventRegistration(db.Model):
    """Model for event registrations."""
    __tablename__ = 'event_registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('library_events.event_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    registration_date = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    status = db.Column(db.Enum('registered', 'attended', 'cancelled', 'no_show'), default='registered', index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

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

    @classmethod
    def get_by_id(cls, registration_id):
        """Get a registration by its ID."""
        return cls.query.get(registration_id)

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

    def to_dict(self):
        """Convert registration to dictionary."""
        return {
            'registration_id': self.registration_id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'event': self.event.to_dict() if self.event else None,
            'user': self.user.to_dict() if self.user else None
        }

    def __repr__(self):
        """String representation of the registration."""
        return f'<EventRegistration {self.registration_id}: {self.event.title if self.event else "Unknown Event"} - {self.user.username if self.user else "Unknown User"}>' 