from extensions import db
from datetime import datetime

class LibraryBranch(db.Model):
    __tablename__ = 'library_branches'
    
    branch_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    opening_hours = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    manager = db.relationship('User', backref='managed_branches')
    book_copies = db.relationship('BookCopy', backref='branch', lazy=True)
    events = db.relationship('LibraryEvent', backref='branch', lazy=True)

    def __init__(self, name, address, phone=None, email=None, opening_hours=None, manager_id=None):
        self.name = name
        self.address = address
        self.phone = phone
        self.email = email
        self.opening_hours = opening_hours
        self.manager_id = manager_id

class MembershipType(db.Model):
    __tablename__ = 'membership_types'
    
    type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    max_books = db.Column(db.Integer, nullable=False, default=5)
    loan_period = db.Column(db.Integer, nullable=False, default=14)  # in days
    renewal_period = db.Column(db.Integer, nullable=False, default=365)  # in days
    fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    memberships = db.relationship('UserMembership', backref='membership_type', lazy=True)

    def __init__(self, name, description=None, max_books=5, loan_period=14, renewal_period=365, fee=0):
        self.name = name
        self.description = description
        self.max_books = max_books
        self.loan_period = loan_period
        self.renewal_period = renewal_period
        self.fee = fee

class UserMembership(db.Model):
    __tablename__ = 'user_memberships'
    
    membership_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('membership_types.type_id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('active', 'expired', 'suspended', 'cancelled'), default='active')
    payment_status = db.Column(db.Enum('paid', 'pending', 'overdue'), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='memberships')

    def __init__(self, user_id, type_id, end_date):
        self.user_id = user_id
        self.type_id = type_id
        self.end_date = end_date

    @classmethod
    def get_active_membership(cls, user_id):
        return cls.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()

    def renew(self, renewal_period):
        self.end_date = datetime.utcnow() + renewal_period
        self.status = 'active'
        db.session.commit()

    def suspend(self):
        self.status = 'suspended'
        db.session.commit()

    def cancel(self):
        self.status = 'cancelled'
        db.session.commit()

class LibraryEvent(db.Model):
    __tablename__ = 'library_events'
    
    event_id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('library_branches.branch_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer)  # in minutes
    capacity = db.Column(db.Integer)
    registration_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy=True)

    def __init__(self, branch_id, title, event_date, description=None, duration=None, 
                 capacity=None, registration_required=False):
        self.branch_id = branch_id
        self.title = title
        self.event_date = event_date
        self.description = description
        self.duration = duration
        self.capacity = capacity
        self.registration_required = registration_required

class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'
    
    registration_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('library_events.event_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    registration_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.Enum('registered', 'attended', 'cancelled', 'no_show'), default='registered')
    notes = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', backref='event_registrations')

    def __init__(self, event_id, user_id):
        self.event_id = event_id
        self.user_id = user_id

    @classmethod
    def get_event_registrations(cls, event_id):
        return cls.query.filter_by(event_id=event_id).all()

    def mark_attended(self):
        self.status = 'attended'
        db.session.commit()

    def cancel(self):
        self.status = 'cancelled'
        db.session.commit() 