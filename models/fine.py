"""
Fine model for the Library Management System.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import CheckConstraint
from models.base_model import BaseModel

class Fine(BaseModel):
    """Model for fines."""
    __tablename__ = 'fines'
    
    fine_id = db.Column(db.Integer, primary_key=True)
    borrowing_id = db.Column(db.Integer, db.ForeignKey('borrowings.borrowing_id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    paid_at = db.Column(db.DateTime, index=True)
    is_paid = db.Column(db.Boolean, default=False, index=True)

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
        self.is_active = True

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

    def to_dict(self, exclude=None, include_relationships=True):
        """Convert fine to dictionary."""
        result = super().to_dict(exclude=exclude, include_relationships=include_relationships)
        
        # Add fine-specific fields
        result['amount'] = float(self.amount) if self.amount else 0.00
        if self.paid_at:
            result['paid_at'] = self.paid_at.isoformat()
            
        return result

    def __repr__(self):
        """String representation of the fine."""
        return f'<Fine {self.fine_id}: ${self.amount}>' 