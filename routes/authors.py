from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.author import Author
from utils.security import permission_required
from utils.validation import validate_json_schema_decorator

authors_bp = Blueprint('authors', __name__)

@authors_bp.route('/api/authors', methods=['GET'])
def get_authors():
    authors = Author.get_all()
    return jsonify([author.to_dict() for author in authors])

@authors_bp.route('/api/authors', methods=['POST'])
@login_required
@permission_required('manage_authors')
@validate_json_schema_decorator({
    'type': 'object',
    'required': ['first_name', 'last_name'],
    'properties': {
        'first_name': {'type': 'string'},
        'last_name': {'type': 'string'},
        'biography': {'type': 'string'},
        'birth_date': {'type': 'string', 'format': 'date'},
        'death_date': {'type': 'string', 'format': 'date'},
        'nationality': {'type': 'string'}
    }
})
def add_author():
    data = request.get_json()
    
    try:
        author = Author.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            biography=data.get('biography'),
            birth_date=data.get('birth_date'),
            death_date=data.get('death_date'),
            nationality=data.get('nationality')
        )
        return jsonify({'success': True, 'author_id': author.author_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@authors_bp.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.get_by_id(author_id)
    if not author:
        return jsonify({'error': 'Author not found'}), 404
    
    return jsonify(author.to_dict())

@authors_bp.route('/api/authors/<int:author_id>', methods=['PUT'])
@login_required
@permission_required('manage_authors')
@validate_json_schema_decorator({
    'type': 'object',
    'properties': {
        'first_name': {'type': 'string'},
        'last_name': {'type': 'string'},
        'biography': {'type': 'string'},
        'birth_date': {'type': 'string', 'format': 'date'},
        'death_date': {'type': 'string', 'format': 'date'},
        'nationality': {'type': 'string'}
    }
})
def update_author(author_id):
    author = Author.get_by_id(author_id)
    if not author:
        return jsonify({'error': 'Author not found'}), 404
    
    data = request.get_json()
    
    try:
        author.update(**data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400 