"""
Base model class to eliminate DRY violations across models
"""

from datetime import UTC, datetime
from models import db
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declared_attr

class BaseModel(db.Model):
    """Base model class with common functionality"""
    __abstract__ = True
    
    @declared_attr
    def created_at(cls):
        return db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    
    @declared_attr
    def updated_at(cls):
        return db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    @declared_attr
    def is_active(cls):
        return db.Column(db.Boolean, default=True, index=True)
    
    def to_dict(self, exclude=None, include_relationships=False):
        """Convert model to dictionary"""
        exclude = exclude or []
        result = {}
        
        # Get column attributes
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
        
        # Include relationships if requested
        if include_relationships:
            mapper = inspect(self.__class__)
            for relationship in mapper.relationships:
                if relationship.key not in exclude:
                    related_obj = getattr(self, relationship.key)
                    if related_obj is not None:
                        if hasattr(related_obj, '__iter__') and not isinstance(related_obj, str):
                            result[relationship.key] = [obj.to_dict() if hasattr(obj, 'to_dict') else str(obj) 
                                                       for obj in related_obj]
                        else:
                            result[relationship.key] = (related_obj.to_dict() 
                                                       if hasattr(related_obj, 'to_dict') 
                                                       else str(related_obj))
        
        return result
    
    @classmethod
    def get_by_id(cls, id_value):
        """Get record by primary key"""
        return cls.query.get(id_value)
    
    @classmethod
    def get_all(cls, active_only=True):
        """Get all records, optionally filtering by active status"""
        query = cls.query
        if active_only and hasattr(cls, 'is_active'):
            query = query.filter_by(is_active=True)
        return query.all()
    
    @classmethod
    def create(cls, **kwargs):
        """Create new record"""
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    def update(self, **kwargs):
        """Update record"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now(UTC)
        db.session.commit()
        return self
    
    def delete(self, soft_delete=True):
        """Delete record (soft delete by default)"""
        if soft_delete and hasattr(self, 'is_active'):
            self.is_active = False
            self.updated_at = datetime.now(UTC)
            db.session.commit()
        else:
            db.session.delete(self)
            db.session.commit()
        return True
    
    def save(self):
        """Save changes to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def __repr__(self):
        """String representation"""
        primary_key = inspect(self.__class__).primary_key[0].name
        primary_value = getattr(self, primary_key)
        return f'<{self.__class__.__name__} {primary_value}>'

class TimestampMixin:
    """Mixin for models that only need timestamps"""
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

class ActiveMixin:
    """Mixin for models that need active/inactive status"""
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    @classmethod
    def get_active(cls):
        """Get only active records"""
        return cls.query.filter_by(is_active=True).all()
    
    def deactivate(self):
        """Deactivate record"""
        self.is_active = False
        if hasattr(self, 'updated_at'):
            self.updated_at = datetime.now(UTC)
        db.session.commit()
    
    def activate(self):
        """Activate record"""
        self.is_active = True
        if hasattr(self, 'updated_at'):
            self.updated_at = datetime.now(UTC)
        db.session.commit()
