from datetime import datetime
from extensions import db

class Author(db.Model):
    __tablename__ = 'authors'
    
    author_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    biography = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    nationality = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    books = db.relationship('Book', secondary='book_authors', back_populates='authors')
    
    def __init__(self, first_name, last_name, biography=None, birth_date=None, death_date=None, nationality=None):
        self.first_name = first_name
        self.last_name = last_name
        self.biography = biography
        self.birth_date = birth_date
        self.death_date = death_date
        self.nationality = nationality
    
    def to_dict(self):
        return {
            'author_id': self.author_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'biography': self.biography,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'death_date': self.death_date.isoformat() if self.death_date else None,
            'nationality': self.nationality,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Author {self.first_name} {self.last_name}>'
