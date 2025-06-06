from extensions import db

class UserPermission(db.Model):
    __tablename__ = 'user_permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('user_permissions', lazy=True))
    permission = db.relationship('Permission', backref=db.backref('user_permissions', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'permission_id': self.permission_id
        } 