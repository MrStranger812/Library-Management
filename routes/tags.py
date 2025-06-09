from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.tag import Tag
from utils.security import permission_required
from utils.validation import validate_json_schema_decorator

tags_bp = Blueprint('tags', __name__)

@tags_bp.route('/api/tags', methods=['GET'])
@login_required
@permission_required('manage_tags')
def get_tags():
    tags = Tag.query.all()
    return jsonify([tag.to_dict() for tag in tags])

@tags_bp.route('/api/tags', methods=['POST'])
@login_required
@permission_required('manage_tags')
@validate_json_schema_decorator({
    'type': 'object',
    'required': ['name'],
    'properties': {
        'name': {'type': 'string'},
        'color': {'type': 'string'}
    }
})
def create_tag():
    data = request.get_json()
    try:
        tag = Tag.create(**data)
        return jsonify({'success': True, 'tag_id': tag.tag_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400 