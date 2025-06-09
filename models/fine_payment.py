"""
Fine Payment model for the Library Management System.
Tracks payments made for library fines.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import CheckConstraint
from models.base_model import BaseModel

class FinePayment(BaseModel):
    """Model for fine payments."""
    __tablename__ = 'fine_payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    fine_id = db.Column(db.Integer, db.ForeignKey('fines.fine_id', ondelete='CASCADE'), nullable=False, index=True)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.Enum('cash', 'card', 'online', 'cheque'), nullable=False, index=True)
    payment_reference = db.Column(db.String(100))
    paid_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    paid_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    notes = db.Column(db.Text)

    # Relationships
    fine = db.relationship('Fine', back_populates='payments')
    paid_by_user = db.relationship('User', backref=db.backref('fine_payments', lazy='dynamic'))

    __table_args__ = (
        CheckConstraint('amount_paid > 0', name='chk_payment_amount_positive'),
    )

    def __init__(self, fine_id, amount_paid, payment_method, paid_by=None, payment_reference=None, notes=None):
        """Initialize a new fine payment."""
        self.fine_id = fine_id
        self.amount_paid = amount_paid
        self.payment_method = payment_method
        self.paid_by = paid_by
        self.payment_reference = payment_reference
        self.notes = notes
        self.is_active = True

    @classmethod
    def get_payments_by_fine(cls, fine_id):
        """Get all payments for a specific fine."""
        return cls.query.filter_by(fine_id=fine_id).order_by(cls.paid_at.desc()).all()

    @classmethod
    def get_payments_by_user(cls, user_id):
        """Get all payments made by a specific user."""
        return cls.query.filter_by(paid_by=user_id).order_by(cls.paid_at.desc()).all()

    def to_dict(self, exclude=None, include_relationships=True):
        """Convert payment to dictionary."""
        result = super().to_dict(exclude=exclude, include_relationships=include_relationships)
        
        # Add payment-specific fields
        result['amount_paid'] = float(self.amount_paid) if self.amount_paid else 0.00
        if self.paid_at:
            result['paid_at'] = self.paid_at.isoformat()
            
        return result

    def __repr__(self):
        """String representation of the payment."""
        return f'<FinePayment {self.payment_id}: ${self.amount_paid}>' 