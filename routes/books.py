from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from models.book import Book
from utils.security import Security
from utils.validation import validate_json_schema_decorator
from routes.generic_crud_routes import CRUDBlueprint

# Create the books blueprint with CRUD functionality
books_crud = CRUDBlueprint(
    name='books',
    model_class=Book,
    permission_prefix='books',
    validation_schemas={
        'create': {
            'type': 'object',
            'required': ['isbn', 'title', 'author', 'category_id'],
            'properties': {
                'isbn': {'type': 'string'},
                'title': {'type': 'string'},
                'author': {'type': 'string'},
                'category_id': {'type': 'integer'},
                'publisher_id': {'type': 'integer'},
                'publication_year': {'type': 'integer'},
                'description': {'type': 'string'},
                'page_count': {'type': 'integer'},
                'language': {'type': 'string'},
                'total_copies': {'type': 'integer', 'minimum': 1}
            }
        }
    }
)

# Add custom routes
@books_crud.blueprint.route('/books')
@login_required
def index():
    """Render the books management page."""
    return render_template('books/index.html')

@books_crud.blueprint.route('/api/books', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_json_schema_decorator({
    'type': 'object',
    'required': ['isbn', 'title', 'author', 'category_id'],
    'properties': {
        'isbn': {'type': 'string'},
        'title': {'type': 'string'},
        'author': {'type': 'string'},
        'category_id': {'type': 'integer'},
        'publisher_id': {'type': 'integer'},
        'publication_year': {'type': 'integer'},
        'description': {'type': 'string'},
        'page_count': {'type': 'integer'},
        'language': {'type': 'string'},
        'total_copies': {'type': 'integer', 'minimum': 1}
    }
})
def api_add_book():
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    try:
        book = Book(
            isbn=data['isbn'],
            title=data['title'],
            author=data['author'],
            category_id=data['category_id'],
            publisher_id=data.get('publisher_id'),
            publication_year=data.get('publication_year'),
            description=data.get('description'),
            page_count=data.get('page_count'),
            language=data.get('language', 'English'),
            total_copies=data.get('total_copies', 1)
        )
        book.added_by = current_user.user_id
        db.session.add(book)
        db.session.commit()
        return jsonify({'success': True, 'book_id': book.book_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@books_crud.blueprint.route('/api/books', methods=['GET'])
def api_get_books():
    query = request.args.get('q', '')
    if query:
        books = Book.search(query)
    else:
        books = Book.get_all()
    
    return jsonify([book.to_dict() for book in books])

@books_crud.blueprint.route('/api/books/<int:book_id>', methods=['GET'])
def api_get_book(book_id):
    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify(book.to_dict())

# Export the blueprint
books_bp = books_crud.blueprint 