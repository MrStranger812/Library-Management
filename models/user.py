from flask_login import UserMixin
from extensions import mysql, bcrypt, login_manager
class User(UserMixin):
    def __init__(self, user_id, username, password, full_name, email, role):
        self.id = user_id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.email = email
        self.role = role
    
    @classmethod
    def get_by_id(cls, user_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            return cls(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5])
        return None
    
    @classmethod
    def get_by_username(cls, username):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data:
            return cls(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5])
        return None
    
    @staticmethod
    def create(username, password, full_name, email, role):
        cursor = mysql.connection.cursor()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute(
            "INSERT INTO users (username, password, full_name, email, role) VALUES (%s, %s, %s, %s, %s)",
            (username, hashed_password, full_name, email, role)
        )
        mysql.connection.commit()
        user_id = cursor.lastrowid
        cursor.close()
        return user_id
    
    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def has_permission(self, permission_name):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT 1 FROM user_permissions up
            JOIN permissions p ON up.permission_id = p.permission_id
            WHERE up.user_id = %s AND p.permission_name = %s
        """, (self.id, permission_name))
        result = cursor.fetchone()
        cursor.close()
        return result is not None


class Permission:
    @staticmethod
    def get_all():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM permissions")
        permissions = cursor.fetchall()
        cursor.close()
        return permissions
    
    @staticmethod
    def grant(user_id, permission_id, granted_by):
        cursor = mysql.connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO user_permissions (user_id, permission_id, granted_by) VALUES (%s, %s, %s)",
                (user_id, permission_id, granted_by)
            )
            mysql.connection.commit()
            cursor.close()
            return True, "Permission granted successfully"
        except Exception as e:
            cursor.close()
            return False, str(e)
    
    @staticmethod
    def revoke(user_id, permission_id):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "DELETE FROM user_permissions WHERE user_id = %s AND permission_id = %s",
            (user_id, permission_id)
        )
        mysql.connection.commit()
        result = cursor.rowcount > 0
        cursor.close()
        return result, "Permission revoked successfully" if result else "Permission was not found"
    
    @staticmethod
    def get_user_permissions(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT p.permission_id, p.permission_name, p.description, up.granted_at, 
                   u.username as granted_by
            FROM user_permissions up
            JOIN permissions p ON up.permission_id = p.permission_id
            JOIN users u ON up.granted_by = u.user_id
            WHERE up.user_id = %s
        """, (user_id,))
        permissions = cursor.fetchall()
        cursor.close()
        return permissions