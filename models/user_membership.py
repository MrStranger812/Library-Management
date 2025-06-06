from datetime import datetime
from extensions import db

class UserMembership(db.Model):
    __tablename__ = 'user_memberships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    membership_type_id = db.Column(db.Integer, db.ForeignKey('membership_types.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('memberships', lazy=True))
    membership_type = db.relationship('MembershipType', backref=db.backref('user_memberships', lazy=True))

    @classmethod
    def get_active_membership(cls, user_id):
        """Get the active membership for a user."""
        return cls.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()

    def to_dict(self):
        """Convert membership to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'membership_type_id': self.membership_type_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 