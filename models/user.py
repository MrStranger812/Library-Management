from flask_login import UserMixin
from extensions import db, bcrypt
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum('admin', 'librarian', 'member'), nullable=False, default='member')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.String(255), nullable=True)

    # Relationships
    borrowings = db.relationship('Borrowing', backref='user', lazy=True)
    reviews = db.relationship('BookReview', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    permissions = db.relationship('UserPermission', backref='user', lazy=True)
    memberships = db.relationship('UserMembership', backref='user', lazy=True)
    preferences = db.relationship('UserPreference', backref='user', lazy=True)

    def __init__(self, username, password, email, full_name, role='member'):
        self.username = username
        self.set_password(password)
        self.email = email
        self.full_name = full_name
        self.role = role

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def get_id(self):
        return str(self.user_id)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.get(user_id)

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def has_permission(self, permission_name):
        return any(p.permission.permission_name == permission_name for p in self.permissions)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    permission_id = db.Column(db.Integer, primary_key=True)
    permission_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user_permissions = db.relationship('UserPermission', backref='permission', lazy=True)

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'
    
    user_permission_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id', ondelete='CASCADE'), nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'permission_id', name='unique_user_permission'),
    )