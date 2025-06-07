"""
UserMembership model for the Library Management System.
Represents a user's membership in the library.
"""

from datetime import UTC, datetime
from models import db

class UserMembership(db.Model):
    __tablename__ = 'user_memberships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    membership_type_id = db.Column(db.Integer, db.ForeignKey('membership_types.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC), index=True)
    end_date = db.Column(db.DateTime, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    user = db.relationship('User', backref=db.backref('memberships', lazy='dynamic', cascade='all, delete-orphan'))
    membership_type = db.relationship('MembershipType', backref=db.backref('user_memberships', lazy='dynamic', cascade='all, delete-orphan'))

    def __init__(self, user_id, membership_type_id, start_date, end_date, is_active=True):
        self.user_id = user_id
        self.membership_type_id = membership_type_id
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active

    @classmethod
    def get_active_membership(cls, user_id):
        """Get the active membership for a user."""
        return cls.query.filter_by(user_id=user_id, is_active=True).first()

    @classmethod
    def get_by_id(cls, id):
        """Get a user membership by its ID."""
        return cls.query.get(id)

    @classmethod
    def get_user_memberships(cls, user_id):
        """Get all memberships for a user."""
        return cls.query.filter_by(user_id=user_id).order_by(cls.start_date.desc()).all()

    def to_dict(self):
        """Convert membership to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'membership_type_id': self.membership_type_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'membership_type': self.membership_type.to_dict() if self.membership_type else None
        }

    def __repr__(self):
        return f'<UserMembership {self.user_id} - {self.membership_type_id}>' 