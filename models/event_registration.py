from datetime import datetime
from extensions import db

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('library_events.event_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    registration_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, cancelled, attended, no_show
    notes = db.Column(db.Text)
    
    # Relationships
    event = db.relationship('LibraryEvent', back_populates='registrations')
    user = db.relationship('User', backref='event_registrations')
    
    def __init__(self, event_id, user_id, status='registered', notes=None):
        self.event_id = event_id
        self.user_id = user_id
        self.status = status
        self.notes = notes
    
    def to_dict(self):
        return {
            'registration_id': self.registration_id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'registration_time': self.registration_time.isoformat() if self.registration_time else None,
            'status': self.status,
            'notes': self.notes,
            'event': self.event.to_dict() if self.event else None,
            'user': {
                'username': self.user.username,
                'full_name': self.user.full_name
            } if self.user else None
        }
    
    def __repr__(self):
        return f'<EventRegistration {self.registration_id}: {self.status}>' 