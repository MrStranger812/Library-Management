from datetime import datetime
from extensions import db
from models.user import User

class LibraryEvent(db.Model):
    __tablename__ = 'library_events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    event_type = db.Column(db.String(50), nullable=False)  # workshop, lecture, book_club, etc.
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100))
    capacity = db.Column(db.Integer)
    registration_deadline = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_events')
    registrations = db.relationship('EventRegistration', back_populates='event', cascade='all, delete-orphan')
    
    def __init__(self, title, event_type, start_time, end_time, description=None, location=None, 
                 capacity=None, registration_deadline=None, created_by=None):
        self.title = title
        self.event_type = event_type
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.location = location
        self.capacity = capacity
        self.registration_deadline = registration_deadline
        self.created_by = created_by
    
    @property
    def is_registration_open(self):
        if not self.registration_deadline:
            return True
        return datetime.utcnow() < self.registration_deadline
    
    @property
    def is_full(self):
        if not self.capacity:
            return False
        return len(self.registrations) >= self.capacity
    
    @property
    def available_spots(self):
        if not self.capacity:
            return float('inf')
        return max(0, self.capacity - len(self.registrations))
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location': self.location,
            'capacity': self.capacity,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_registration_open': self.is_registration_open,
            'is_full': self.is_full,
            'available_spots': self.available_spots,
            'registrations_count': len(self.registrations)
        }
    
    def __repr__(self):
        return f'<LibraryEvent {self.title}>' 