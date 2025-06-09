"""
Fine model for the Library Management System.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import CheckConstraint

class Fine(db.Model):
    """Model for fines."""
    __tablename__ = 'fines'
    
    fine_id = db.Column(db.Integer, primary_key=True)
    borrowing_id = db.Column(db.Integer, db.ForeignKey('borrowings.borrowing_id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    paid_at = db.Column(db.DateTime, index=True)
    is_paid = db.Column(db.Boolean, default=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    borrowing = db.relationship('Borrowing', back_populates='fines')
    payments = db.relationship('FinePayment', back_populates='fine', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('amount >= 0', name='chk_fine_amount_positive'),
    )

    def __init__(self, borrowing_id, amount, reason):
        """Initialize a new fine."""
        self.borrowing_id = borrowing_id
        self.amount = amount
        self.reason = reason
        self.is_paid = False

    @classmethod
    def get_unpaid_fines(cls):
        """Get all unpaid fines."""
        return cls.query.filter_by(is_paid=False).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_user_fines(cls, user_id):
        """Get all fines for a specific user."""
        return cls.query.join(cls.borrowing).filter(cls.borrowing.user_id == user_id).order_by(cls.created_at.desc()).all()

    def mark_as_paid(self):
        """Mark the fine as paid."""
        self.is_paid = True
        self.paid_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        db.session.commit()

    def to_dict(self):
        """Convert fine to dictionary."""
        return {
            'fine_id': self.fine_id,
            'borrowing_id': self.borrowing_id,
            'amount': float(self.amount) if self.amount else 0.00,
            'reason': self.reason,
            'is_paid': self.is_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'payments': [payment.to_dict() for payment in self.payments]
        }

    def __repr__(self):
        """String representation of the fine."""
        return f'<Fine {self.fine_id}: ${self.amount}>' 