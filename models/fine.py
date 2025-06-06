from datetime import datetime
from extensions import db

class Fine(db.Model):
    __tablename__ = 'fines'
    
    fine_id = db.Column(db.Integer, primary_key=True)
    borrowing_id = db.Column(db.Integer, db.ForeignKey('borrowings.borrowing_id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    is_paid = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(50))
    payment_reference = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Relationships
    borrowing = db.relationship('Borrowing', backref=db.backref('fines', lazy='dynamic'))
    
    def __init__(self, borrowing_id, amount, reason, notes=None):
        self.borrowing_id = borrowing_id
        self.amount = amount
        self.reason = reason
        self.notes = notes
    
    def to_dict(self):
        return {
            'fine_id': self.fine_id,
            'borrowing_id': self.borrowing_id,
            'amount': float(self.amount),
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'is_paid': self.is_paid,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'notes': self.notes
        }
    
    def pay(self, payment_method, payment_reference=None, notes=None):
        """Mark the fine as paid."""
        self.is_paid = True
        self.paid_at = datetime.utcnow()
        self.payment_method = payment_method
        self.payment_reference = payment_reference
        if notes:
            self.notes = notes
    
    def waive(self, notes=None):
        """Waive the fine."""
        self.is_paid = True
        self.paid_at = datetime.utcnow()
        self.payment_method = 'waived'
        if notes:
            self.notes = notes
    
    @classmethod
    def calculate_fine(cls, borrowing):
        """Calculate fine amount for a borrowing."""
        if not borrowing.is_overdue():
            return 0
        
        days_overdue = borrowing.get_days_overdue()
        fine_rate = 0.50  # $0.50 per day
        return days_overdue * fine_rate
    
    @classmethod
    def create_for_borrowing(cls, borrowing, notes=None):
        """Create a fine for an overdue borrowing."""
        amount = cls.calculate_fine(borrowing)
        if amount > 0:
            fine = cls(
                borrowing_id=borrowing.borrowing_id,
                amount=amount,
                reason=f'Overdue by {borrowing.get_days_overdue()} days',
                notes=notes
            )
            db.session.add(fine)
            db.session.commit()
            return fine
        return None
    
    def __repr__(self):
        return f'<Fine {self.fine_id}: ${self.amount}>' 