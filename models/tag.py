from datetime import datetime
from extensions import db

class Tag(db.Model):
    __tablename__ = 'tags'
    
    tag_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6c757d')  # Hex color code
    created_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    books = db.relationship('Book', secondary='book_tags', backref=db.backref('tags', lazy='dynamic'))
    creator = db.relationship('User', backref=db.backref('created_tags', lazy='dynamic'))
    
    def __init__(self, name, description=None, color='#6c757d', created_by=None):
        self.name = name
        self.description = description
        self.color = color
        self.created_by = created_by
    
    def to_dict(self):
        return {
            'tag_id': self.tag_id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'book_count': self.books.count()
        }
    
    @classmethod
    def get_by_name(cls, name):
        """Get a tag by its name."""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_or_create(cls, name, description=None, color='#6c757d', created_by=None):
        """Get a tag by name or create it if it doesn't exist."""
        tag = cls.get_by_name(name)
        if not tag:
            tag = cls(name=name, description=description, color=color, created_by=created_by)
            db.session.add(tag)
            db.session.commit()
        return tag
    
    def update(self, **kwargs):
        """Update tag attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def delete(self):
        """Delete the tag and its associations."""
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        return f'<Tag {self.name}>' 