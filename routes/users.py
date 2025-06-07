from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.user import User
from utils.security import permission_required
from utils.middleware import validate_json_schema

users_bp = Blueprint('users', __name__)

@users_bp.route('/api/users', methods=['GET'])
@login_required
@permission_required('manage_users')
def get_users():
    users = User.get_all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/api/users', methods=['POST'])
@login_required
@permission_required('manage_users')
@validate_json_schema({
    'type': 'object',
    'required': ['username', 'password', 'full_name', 'email', 'role'],
    'properties': {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'full_name': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'},
        'role': {'type': 'string', 'enum': ['admin', 'librarian', 'member']}
    }
})
def add_user():
    data = request.get_json()
    
    # Validate password
    is_valid, message = Security.validate_password(data['password'])
    if not is_valid:
        return jsonify({'success': False, 'message': message}), 400
    
    # Check if user already exists
    if User.get_by_username(data['username']):
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    try:
        user = User.create(
            username=data['username'],
            password=data['password'],
            full_name=data['full_name'],
            email=data['email'],
            role=data['role']
        )
        return jsonify({'success': True, 'user_id': user.user_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400 