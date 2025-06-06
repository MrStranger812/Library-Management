from extensions import db

class MembershipType(db.Model):
    __tablename__ = 'membership_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    max_books = db.Column(db.Integer, nullable=False, default=3)
    max_days = db.Column(db.Integer, nullable=False, default=14)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        """Convert membership type to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'max_books': self.max_books,
            'max_days': self.max_days,
            'price': float(self.price),
            'is_active': self.is_active
        } 