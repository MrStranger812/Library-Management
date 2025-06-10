from flask import render_template, jsonify, request
from flask_login import login_required, current_user
from models.notification import UserPreference
from models.preferences import Preferences
from utils.security import permission_required
from utils.validation import validate_json_schema_decorator
from utils.error_handler import handle_error
from routes.generic_crud_routes import CRUDBlueprint

# Create the preferences blueprint with CRUD functionality
preferences_crud = CRUDBlueprint(
    name='preferences',
    model_class=UserPreference,
    permission_prefix='preferences',
    validation_schemas={
        'update': {
            'type': 'object',
            'properties': {
                'email_notifications': {'type': 'boolean'},
                'sms_notifications': {'type': 'boolean'},
                'notification_types': {'type': 'object'},
                'theme': {'type': 'string'},
                'language': {'type': 'string'},
                'items_per_page': {'type': 'integer'},
                'show_cover_images': {'type': 'boolean'},
                'default_search_type': {'type': 'string'},
                'show_reading_history': {'type': 'boolean'},
                'show_reviews': {'type': 'boolean'},
                'allow_recommendations': {'type': 'boolean'}
            }
        }
    }
)

# Add custom routes
@preferences_crud.blueprint.route('/preferences')
@permission_required('admin')
def index():
    """Render the preferences management page."""
    return render_template('preferences/index.html')

@preferences_crud.blueprint.route('/api/preferences', methods=['GET'])
@login_required
@permission_required('manage_preferences')
def get_user_preferences():
    prefs = UserPreference.get_by_user(current_user.user_id)
    return jsonify(prefs.to_dict() if prefs else {})

@preferences_crud.blueprint.route('/api/preferences', methods=['PUT'])
@login_required
@permission_required('manage_preferences')
@validate_json_schema_decorator({
    'type': 'object',
    'properties': {
        'email_notifications': {'type': 'boolean'},
        'sms_notifications': {'type': 'boolean'},
        'notification_types': {'type': 'object'},
        'theme': {'type': 'string'},
        'language': {'type': 'string'},
        'items_per_page': {'type': 'integer'},
        'show_cover_images': {'type': 'boolean'},
        'default_search_type': {'type': 'string'},
        'show_reading_history': {'type': 'boolean'},
        'show_reviews': {'type': 'boolean'},
        'allow_recommendations': {'type': 'boolean'}
    }
})
def update_preferences():
    data = request.get_json()
    try:
        prefs = UserPreference.update_or_create(current_user.user_id, **data)
        return jsonify({'success': True, 'preferences': prefs.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

# Export the blueprint
preferences_bp = preferences_crud.blueprint 