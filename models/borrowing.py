# Borrowing model in models/borrowing.py
from extensions import db
from datetime import datetime

class Borrowing(db.Model):
    __tablename__ = 'borrowings'
    
    borrowing_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    copy_id = db.Column(db.Integer, db.ForeignKey('book_copies.copy_id', ondelete='SET NULL'))
    borrow_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.Enum('borrowed', 'returned', 'overdue', 'lost'), default='borrowed')
    fine_amount = db.Column(db.Numeric(10, 2), default=0)
    notes = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', backref='borrowings')
    book = db.relationship('Book', backref='borrowings')
    copy = db.relationship('BookCopy', backref='borrowings')
    fine_payments = db.relationship('FinePayment', backref='borrowing', lazy=True)

    def __init__(self, user_id, book_id, due_date, copy_id=None):
        self.user_id = user_id
        self.book_id = book_id
        self.due_date = due_date
        self.copy_id = copy_id

    @classmethod
    def get_by_id(cls, borrowing_id):
        return cls.query.get(borrowing_id)

    @classmethod
    def get_user_borrowings(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_overdue_borrowings(cls):
        return cls.query.filter(
            cls.status == 'borrowed',
            cls.due_date < datetime.utcnow()
        ).all()

    def calculate_fine(self):
        if self.status == 'borrowed' and self.due_date < datetime.utcnow():
            days_overdue = (datetime.utcnow() - self.due_date).days
            self.fine_amount = days_overdue * 1.0  # $1 per day
            self.status = 'overdue'
            db.session.commit()

    def return_book(self):
        self.return_date = datetime.utcnow()
        self.status = 'returned'
        if self.copy:
            self.copy.is_available = True
        db.session.commit()

class FinePayment(db.Model):
    __tablename__ = 'fine_payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    borrowing_id = db.Column(db.Integer, db.ForeignKey('borrowings.borrowing_id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    payment_method = db.Column(db.Enum('cash', 'credit_card', 'debit_card', 'online'), nullable=False)
    transaction_id = db.Column(db.String(100))
    notes = db.Column(db.Text)

    def __init__(self, borrowing_id, amount, payment_method, transaction_id=None):
        self.borrowing_id = borrowing_id
        self.amount = amount
        self.payment_method = payment_method
        self.transaction_id = transaction_id

class Reservation(db.Model):
    __tablename__ = 'reservations'
    
    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    reservation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('pending', 'fulfilled', 'expired', 'cancelled'), default='pending')
    priority = db.Column(db.Integer, default=1)
    notes = db.Column(db.Text)

    # Relationships
    user = db.relationship('User', backref='reservations')
    book = db.relationship('Book', backref='reservations')

    def __init__(self, user_id, book_id, expiry_date):
        self.user_id = user_id
        self.book_id = book_id
        self.expiry_date = expiry_date

    @classmethod
    def get_by_id(cls, reservation_id):
        return cls.query.get(reservation_id)

    @classmethod
    def get_user_reservations(cls, user_id):
        return cls.query.filter_by(user_id=user_id).all()

    @classmethod
    def get_pending_reservations(cls, book_id):
        return cls.query.filter_by(
            book_id=book_id,
            status='pending'
        ).order_by(cls.priority.desc(), cls.reservation_date.asc()).all()

    def cancel(self):
        self.status = 'cancelled'
        db.session.commit()

    def fulfill(self):
        self.status = 'fulfilled'
        db.session.commit()