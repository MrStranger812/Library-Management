from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from models.user import User
from utils.security import permission_required, Security
from utils.validation import validate_json_schema_decorator
from routes.generic_crud_routes import CRUDBlueprint

# Create the users blueprint with CRUD functionality
users_crud = CRUDBlueprint(
    name='users',
    model_class=User,
    permission_prefix='users',
    validation_schemas={
        'create': {
            'type': 'object',
            'required': ['username', 'email', 'password'],
            'properties': {
                'username': {'type': 'string'},
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string', 'minLength': 8},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'}
            }
        }
    }
)

# Add custom routes
@users_crud.blueprint.route('/users')
@login_required
@permission_required('manage_users')
def index():
    """Render the users management page."""
    return render_template('users/index.html')

@users_crud.blueprint.route('/api/users', methods=['POST'])
@login_required
@permission_required('manage_users')
@validate_json_schema_decorator({
    'type': 'object',
    'required': ['username', 'email', 'password'],
    'properties': {
        'username': {'type': 'string'},
        'email': {'type': 'string', 'format': 'email'},
        'password': {'type': 'string', 'minLength': 8},
        'first_name': {'type': 'string'},
        'last_name': {'type': 'string'}
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
            full_name=data['first_name'] + ' ' + data['last_name'],
            email=data['email'],
            role='member'
        )
        return jsonify({'success': True, 'user_id': user.user_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# Export the blueprint
users_bp = users_crud.blueprint 