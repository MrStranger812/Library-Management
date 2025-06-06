from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from database import config as db_config
import os
from extensions import bcrypt, login_manager
from utils.security import Security
from utils.middleware import security_headers, validate_request, require_https, validate_json_schema, log_request, handle_cors
from datetime import datetime, timedelta
from flask_expects_json import expects_json
from flask_expects_json.exceptions import ValidationError

app = Flask(__name__)

# Load SQLAlchemy config from database/config.py
app.config['SQLALCHEMY_DATABASE_URI'] = db_config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = db_config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ECHO'] = db_config.SQLALCHEMY_ECHO
app.config.update(db_config.SQLALCHEMY_ENGINE_OPTIONS)

# Initialize SQLAlchemy
# Make db available for models
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy db instance
# (This should be imported in your models as well)
db = SQLAlchemy(app)

# Initialize other extensions
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models (update these to use SQLAlchemy in the next step)
from models.user import User
from models.book import Book
from models.borrowing import Borrowing
from models.user import Permission
from models.user_membership import UserMembership
from models.user_permission import UserPermission
from models.author import Author
from models.book_author import BookAuthor
from models.book_review import BookReview
from models.library_event import LibraryEvent
from models.event_registration import EventRegistration
from models.user_preference import UserPreference
from models.tag import Tag
from models.book_tag import BookTag
from models.fine import Fine
from models.audit_log import AuditLog

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Apply security middleware to all routes
@app.before_request
def before_request():
    Security.check_ip_rate_limit()

# Routes
@app.route('/register', methods=['GET', 'POST'])
@validate_request()
@security_headers()
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']
        
        # Validate password
        is_valid, message = Security.validate_password(password)
        if not is_valid:
            flash(message, 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('register.html')
        
        # Create user with default role
        User.create(username, password, full_name, email, 'member')
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
@validate_request()
@security_headers()
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check for account lockout
        is_locked, message = Security.check_login_attempts(username)
        if is_locked:
            flash(message, 'danger')
            return render_template('login.html')
        
        user = User.get_by_username(username)
        
        if user and user.verify_password(password):
            Security.record_login_attempt(username, True)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            Security.record_login_attempt(username, False)
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
@security_headers()
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
@security_headers()
def dashboard():
    return render_template('dashboard.html')

# API Routes
@app.route('/api/books', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
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

@app.route('/api/books', methods=['GET'])
def api_get_books():
    query = request.args.get('q', '')
    if query:
        books = Book.search(query)
    else:
        books = Book.get_all()
    
    return jsonify([book.to_dict() for book in books])

@app.route('/api/books/<int:book_id>', methods=['GET'])
def api_get_book(book_id):
    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    return jsonify(book.to_dict())

@app.route('/api/books/<int:book_id>', methods=['PUT'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'properties': {
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
def api_update_book(book_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(book, key, value)
        db.session.commit()
        return jsonify({'success': True, 'book': book.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_delete_book(book_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/users', methods=['GET'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_get_users():
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403

    users = User.query.all()
    return jsonify([{
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    } for user in users])

@app.route('/api/users', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
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
def api_add_user():
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403

    data = request.get_json()

    # Check if username or email already exists
    if User.get_by_username(data['username']):
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    if User.get_by_email(data['email']):
        return jsonify({'success': False, 'message': 'Email already exists'}), 400

    try:
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            role=data['role']
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()

        # Assign default permissions based on role
        if data['role'] == 'admin':
            permissions = Permission.query.all()
        elif data['role'] == 'librarian':
            permissions = Permission.query.filter(Permission.name.in_(['manage_books', 'manage_borrowings'])).all()
        else:  # member
            permissions = Permission.query.filter_by(name='borrow_books').all()

        for permission in permissions:
            user_permission = UserPermission(
                user_id=user.user_id,
                permission_id=permission.permission_id
            )
            db.session.add(user_permission)
        db.session.commit()

        return jsonify({
            'success': True,
            'user_id': user.user_id,
            'message': 'User created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/borrowings/borrow', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['book_id'],
    'properties': {
        'book_id': {'type': 'integer'},
        'days': {'type': 'integer', 'minimum': 1, 'maximum': 30}
    }
})
def api_borrow_book():
    data = request.get_json()
    book_id = data['book_id']
    days = data.get('days', 14)

    # Get user's active membership
    membership = UserMembership.get_active_membership(current_user.user_id)
    if not membership:
        return jsonify({'success': False, 'message': 'No active membership found'}), 400

    # Check if user has reached their borrowing limit
    active_borrowings = Borrowing.query.filter_by(
        user_id=current_user.user_id,
        status='borrowed'
    ).count()
    if active_borrowings >= membership.membership_type.max_books:
        return jsonify({'success': False, 'message': 'Borrowing limit reached'}), 400

    # Get book and check availability
    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'success': False, 'message': 'Book not found'}), 404
    if book.copies_available <= 0:
        return jsonify({'success': False, 'message': 'Book not available for borrowing'}), 400

    try:
        # Create borrowing record
        due_date = datetime.utcnow() + timedelta(days=days)
        borrowing = Borrowing(
            user_id=current_user.user_id,
            book_id=book_id,
            due_date=due_date
        )
        db.session.add(borrowing)

        # Update book availability
        book.copies_available -= 1
        db.session.commit()

        return jsonify({
            'success': True,
            'borrowing_id': borrowing.borrowing_id,
            'due_date': due_date.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/borrowings/return', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['borrowing_id'],
    'properties': {
        'borrowing_id': {'type': 'integer'}
    }
})
def api_return_book():
    data = request.get_json()
    borrowing_id = data['borrowing_id']

    borrowing = Borrowing.get_by_id(borrowing_id)
    if not borrowing:
        return jsonify({'success': False, 'message': 'Borrowing record not found'}), 404
    if borrowing.user_id != current_user.user_id and not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    if borrowing.status != 'borrowed':
        return jsonify({'success': False, 'message': 'Book already returned'}), 400

    try:
        # Calculate fine if overdue
        borrowing.calculate_fine()

        # Return the book
        borrowing.return_book()

        # Update book availability
        book = borrowing.book
        book.copies_available += 1
        db.session.commit()

        response = {'success': True}
        if borrowing.fine_amount > 0:
            response['fine_amount'] = float(borrowing.fine_amount)
        return jsonify(response)
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/borrowings/user', methods=['GET'])
@login_required
def api_get_user_borrowings():
    borrowings = Borrowing.get_user_borrowings(current_user.user_id)
    return jsonify([{
        'borrowing_id': b.borrowing_id,
        'book': b.book.to_dict(),
        'borrow_date': b.borrow_date.isoformat(),
        'due_date': b.due_date.isoformat(),
        'return_date': b.return_date.isoformat() if b.return_date else None,
        'status': b.status,
        'fine_amount': float(b.fine_amount) if b.fine_amount else 0
    } for b in borrowings])

@app.route('/api/borrowings/overdue', methods=['GET'])
@login_required
@Security.require_api_key()
def api_get_overdue_borrowings():
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403

    borrowings = Borrowing.get_overdue_borrowings()
    return jsonify([{
        'borrowing_id': b.borrowing_id,
        'user': {
            'user_id': b.user.user_id,
            'username': b.user.username,
            'email': b.user.email
        },
        'book': b.book.to_dict(),
        'borrow_date': b.borrow_date.isoformat(),
        'due_date': b.due_date.isoformat(),
        'days_overdue': (datetime.utcnow() - b.due_date).days,
        'fine_amount': float(b.fine_amount) if b.fine_amount else 0
    } for b in borrowings])

@app.route('/api/permissions', methods=['GET'])
@login_required
def api_get_permissions():
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403

    permissions = Permission.query.all()
    return jsonify([{
        'permission_id': p.permission_id,
        'name': p.name,
        'description': p.description
    } for p in permissions])

@app.route('/api/permissions/grant', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['user_id', 'permission_id'],
    'properties': {
        'user_id': {'type': 'integer'},
        'permission_id': {'type': 'integer'}
    }
})
def api_grant_permission():
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403

    data = request.get_json()
    user_id = data['user_id']
    permission_id = data['permission_id']

    # Check if user and permission exist
    user = User.get_by_id(user_id)
    permission = Permission.query.get(permission_id)
    if not user or not permission:
        return jsonify({'success': False, 'message': 'User or permission not found'}), 404

    # Check if permission is already granted
    existing = UserPermission.query.filter_by(
        user_id=user_id,
        permission_id=permission_id
    ).first()
    if existing:
        return jsonify({'success': False, 'message': 'Permission already granted'}), 400

    try:
        user_permission = UserPermission(
            user_id=user_id,
            permission_id=permission_id
        )
        db.session.add(user_permission)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Permission granted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/permissions/revoke', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['user_id', 'permission_id'],
    'properties': {
        'user_id': {'type': 'integer'},
        'permission_id': {'type': 'integer'}
    }
})
def api_revoke_permission():
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403

    data = request.get_json()
    user_id = data['user_id']
    permission_id = data['permission_id']

    # Check if user and permission exist
    user = User.get_by_id(user_id)
    permission = Permission.query.get(permission_id)
    if not user or not permission:
        return jsonify({'success': False, 'message': 'User or permission not found'}), 404

    # Check if permission is granted
    user_permission = UserPermission.query.filter_by(
        user_id=user_id,
        permission_id=permission_id
    ).first()
    if not user_permission:
        return jsonify({'success': False, 'message': 'Permission not granted'}), 400

    try:
        db.session.delete(user_permission)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Permission revoked successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Author Management Routes
@app.route('/api/authors', methods=['GET'])
def api_get_authors():
    query = request.args.get('q', '')
    if query:
        authors = Author.query.filter(
            (Author.first_name.ilike(f'%{query}%')) |
            (Author.last_name.ilike(f'%{query}%'))
        ).all()
    else:
        authors = Author.query.all()
    
    return jsonify([{
        'author_id': author.author_id,
        'first_name': author.first_name,
        'last_name': author.last_name,
        'biography': author.biography,
        'birth_date': author.birth_date.isoformat() if author.birth_date else None,
        'death_date': author.death_date.isoformat() if author.death_date else None,
        'nationality': author.nationality,
        'books': [book.to_dict() for book in author.books]
    } for author in authors])

@app.route('/api/authors', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
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
def api_add_author():
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    try:
        author = Author(
            first_name=data['first_name'],
            last_name=data['last_name'],
            biography=data.get('biography'),
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            death_date=datetime.strptime(data['death_date'], '%Y-%m-%d').date() if data.get('death_date') else None,
            nationality=data.get('nationality')
        )
        db.session.add(author)
        db.session.commit()
        return jsonify({'success': True, 'author_id': author.author_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/authors/<int:author_id>', methods=['GET'])
def api_get_author(author_id):
    author = Author.query.get(author_id)
    if not author:
        return jsonify({'error': 'Author not found'}), 404
    
    return jsonify({
        'author_id': author.author_id,
        'first_name': author.first_name,
        'last_name': author.last_name,
        'biography': author.biography,
        'birth_date': author.birth_date.isoformat() if author.birth_date else None,
        'death_date': author.death_date.isoformat() if author.death_date else None,
        'nationality': author.nationality,
        'books': [book.to_dict() for book in author.books]
    })

@app.route('/api/authors/<int:author_id>', methods=['PUT'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
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
def api_update_author(author_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    author = Author.query.get(author_id)
    if not author:
        return jsonify({'error': 'Author not found'}), 404
    
    data = request.get_json()
    try:
        if 'first_name' in data:
            author.first_name = data['first_name']
        if 'last_name' in data:
            author.last_name = data['last_name']
        if 'biography' in data:
            author.biography = data['biography']
        if 'birth_date' in data:
            author.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data['birth_date'] else None
        if 'death_date' in data:
            author.death_date = datetime.strptime(data['death_date'], '%Y-%m-%d').date() if data['death_date'] else None
        if 'nationality' in data:
            author.nationality = data['nationality']
        
        db.session.commit()
        return jsonify({'success': True, 'author': {
            'author_id': author.author_id,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'biography': author.biography,
            'birth_date': author.birth_date.isoformat() if author.birth_date else None,
            'death_date': author.death_date.isoformat() if author.death_date else None,
            'nationality': author.nationality
        }})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/authors/<int:author_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_delete_author(author_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    author = Author.query.get(author_id)
    if not author:
        return jsonify({'error': 'Author not found'}), 404
    
    try:
        db.session.delete(author)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/books/<int:book_id>/authors', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['author_id'],
    'properties': {
        'author_id': {'type': 'integer'},
        'role': {'type': 'string', 'enum': ['author', 'co-author', 'editor', 'translator']}
    }
})
def api_add_book_author(book_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    data = request.get_json()
    author = Author.query.get(data['author_id'])
    if not author:
        return jsonify({'error': 'Author not found'}), 404
    
    try:
        book_author = BookAuthor(
            book_id=book_id,
            author_id=data['author_id'],
            role=data.get('role', 'author')
        )
        db.session.add(book_author)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/books/<int:book_id>/authors/<int:author_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_remove_book_author(book_id, author_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    book_author = BookAuthor.query.filter_by(
        book_id=book_id,
        author_id=author_id
    ).first()
    
    if not book_author:
        return jsonify({'error': 'Book-Author relationship not found'}), 404
    
    try:
        db.session.delete(book_author)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Author Routes
@app.route('/authors')
def authors():
    query = request.args.get('q', '')
    if query:
        authors = Author.query.filter(
            (Author.first_name.ilike(f'%{query}%')) |
            (Author.last_name.ilike(f'%{query}%'))
        ).all()
    else:
        authors = Author.query.all()
    return render_template('authors/list.html', authors=authors)

@app.route('/authors/<int:author_id>')
def author_detail(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('authors/detail.html', author=author)

# Book Review Routes
@app.route('/api/books/<int:book_id>/reviews', methods=['GET'])
def api_get_book_reviews(book_id):
    reviews = BookReview.query.filter_by(book_id=book_id).order_by(BookReview.created_at.desc()).all()
    return jsonify([review.to_dict() for review in reviews])

@app.route('/api/books/<int:book_id>/reviews', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['rating'],
    'properties': {
        'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
        'review_text': {'type': 'string'}
    }
})
def api_add_book_review(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    # Check if user has already reviewed this book
    existing_review = BookReview.query.filter_by(
        book_id=book_id,
        user_id=current_user.user_id
    ).first()
    
    if existing_review:
        return jsonify({
            'success': False,
            'message': 'You have already reviewed this book'
        }), 400
    
    try:
        review = BookReview(
            book_id=book_id,
            user_id=current_user.user_id,
            rating=data['rating'],
            review_text=data.get('review_text')
        )
        db.session.add(review)
        db.session.commit()
        return jsonify({'success': True, 'review': review.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/books/<int:book_id>/reviews/<int:review_id>', methods=['PUT'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['rating'],
    'properties': {
        'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
        'review_text': {'type': 'string'}
    }
})
def api_update_book_review(book_id, review_id):
    review = BookReview.query.filter_by(
        book_id=book_id,
        review_id=review_id,
        user_id=current_user.user_id
    ).first_or_404()
    
    data = request.get_json()
    try:
        review.rating = data['rating']
        if 'review_text' in data:
            review.review_text = data['review_text']
        db.session.commit()
        return jsonify({'success': True, 'review': review.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/books/<int:book_id>/reviews/<int:review_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_delete_book_review(book_id, review_id):
    review = BookReview.query.filter_by(
        book_id=book_id,
        review_id=review_id,
        user_id=current_user.user_id
    ).first_or_404()
    
    try:
        db.session.delete(review)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Library Event Routes
@app.route('/events')
def events():
    query = request.args.get('q', '')
    event_type = request.args.get('type', '')
    
    events_query = LibraryEvent.query
    
    if query:
        events_query = events_query.filter(
            (LibraryEvent.title.ilike(f'%{query}%')) |
            (LibraryEvent.description.ilike(f'%{query}%'))
        )
    
    if event_type:
        events_query = events_query.filter_by(event_type=event_type)
    
    events = events_query.order_by(LibraryEvent.start_time).all()
    return render_template('events/list.html', events=events)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = LibraryEvent.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)

@app.route('/api/events', methods=['GET'])
def api_get_events():
    query = request.args.get('q', '')
    event_type = request.args.get('type', '')
    
    events_query = LibraryEvent.query
    
    if query:
        events_query = events_query.filter(
            (LibraryEvent.title.ilike(f'%{query}%')) |
            (LibraryEvent.description.ilike(f'%{query}%'))
        )
    
    if event_type:
        events_query = events_query.filter_by(event_type=event_type)
    
    events = events_query.order_by(LibraryEvent.start_time).all()
    return jsonify([event.to_dict() for event in events])

@app.route('/api/events', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['title', 'event_type', 'start_time', 'end_time'],
    'properties': {
        'title': {'type': 'string'},
        'description': {'type': 'string'},
        'event_type': {'type': 'string'},
        'start_time': {'type': 'string', 'format': 'date-time'},
        'end_time': {'type': 'string', 'format': 'date-time'},
        'location': {'type': 'string'},
        'capacity': {'type': 'integer', 'minimum': 1},
        'registration_deadline': {'type': 'string', 'format': 'date-time'}
    }
})
def api_add_event():
    if not current_user.has_permission('manage_events'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    try:
        event = LibraryEvent(
            title=data['title'],
            event_type=data['event_type'],
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            description=data.get('description'),
            location=data.get('location'),
            capacity=data.get('capacity'),
            registration_deadline=datetime.fromisoformat(data['registration_deadline']) if data.get('registration_deadline') else None,
            created_by=current_user.user_id
        )
        db.session.add(event)
        db.session.commit()
        return jsonify({'success': True, 'event': event.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'properties': {
        'title': {'type': 'string'},
        'description': {'type': 'string'},
        'event_type': {'type': 'string'},
        'start_time': {'type': 'string', 'format': 'date-time'},
        'end_time': {'type': 'string', 'format': 'date-time'},
        'location': {'type': 'string'},
        'capacity': {'type': 'integer', 'minimum': 1},
        'registration_deadline': {'type': 'string', 'format': 'date-time'}
    }
})
def api_update_event(event_id):
    if not current_user.has_permission('manage_events'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    event = LibraryEvent.query.get_or_404(event_id)
    data = request.get_json()
    
    try:
        if 'title' in data:
            event.title = data['title']
        if 'description' in data:
            event.description = data['description']
        if 'event_type' in data:
            event.event_type = data['event_type']
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'])
        if 'end_time' in data:
            event.end_time = datetime.fromisoformat(data['end_time'])
        if 'location' in data:
            event.location = data['location']
        if 'capacity' in data:
            event.capacity = data['capacity']
        if 'registration_deadline' in data:
            event.registration_deadline = datetime.fromisoformat(data['registration_deadline']) if data['registration_deadline'] else None
        
        db.session.commit()
        return jsonify({'success': True, 'event': event.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_delete_event(event_id):
    if not current_user.has_permission('manage_events'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    event = LibraryEvent.query.get_or_404(event_id)
    
    try:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/events/<int:event_id>/register', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_register_for_event(event_id):
    event = LibraryEvent.query.get_or_404(event_id)
    
    if not event.is_registration_open:
        return jsonify({
            'success': False,
            'message': 'Registration is closed for this event'
        }), 400
    
    if event.is_full:
        return jsonify({
            'success': False,
            'message': 'Event is full'
        }), 400
    
    # Check if user is already registered
    existing_registration = EventRegistration.query.filter_by(
        event_id=event_id,
        user_id=current_user.user_id
    ).first()
    
    if existing_registration:
        return jsonify({
            'success': False,
            'message': 'You are already registered for this event'
        }), 400
    
    try:
        registration = EventRegistration(
            event_id=event_id,
            user_id=current_user.user_id
        )
        db.session.add(registration)
        db.session.commit()
        return jsonify({'success': True, 'registration': registration.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/events/<int:event_id>/registrations/<int:registration_id>', methods=['PUT'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['status'],
    'properties': {
        'status': {'type': 'string', 'enum': ['registered', 'cancelled', 'attended', 'no_show']},
        'notes': {'type': 'string'}
    }
})
def api_update_registration(event_id, registration_id):
    registration = EventRegistration.query.filter_by(
        event_id=event_id,
        registration_id=registration_id
    ).first_or_404()
    
    # Only allow users to update their own registrations or admins to update any
    if registration.user_id != current_user.user_id and not current_user.has_permission('manage_events'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    try:
        registration.status = data['status']
        if 'notes' in data:
            registration.notes = data['notes']
        db.session.commit()
        return jsonify({'success': True, 'registration': registration.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/events/<int:event_id>/registrations/<int:registration_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_cancel_registration(event_id, registration_id):
    registration = EventRegistration.query.filter_by(
        event_id=event_id,
        registration_id=registration_id
    ).first_or_404()
    
    # Only allow users to cancel their own registrations or admins to cancel any
    if registration.user_id != current_user.user_id and not current_user.has_permission('manage_events'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        db.session.delete(registration)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# User Preferences Routes
@app.route('/preferences')
@login_required
def preferences():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
        db.session.commit()
    return render_template('preferences/index.html', preferences=user_prefs)

@app.route('/api/preferences', methods=['GET'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_get_preferences():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
        db.session.commit()
    return jsonify(user_prefs.to_dict())

@app.route('/api/preferences', methods=['PUT'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'properties': {
        'email_notifications': {'type': 'boolean'},
        'sms_notifications': {'type': 'boolean'},
        'notification_types': {
            'type': 'object',
            'properties': {
                'due_date': {'type': 'boolean'},
                'overdue': {'type': 'boolean'},
                'reservation': {'type': 'boolean'},
                'system': {'type': 'boolean'}
            }
        },
        'theme': {'type': 'string', 'enum': ['light', 'dark', 'system']},
        'language': {'type': 'string'},
        'items_per_page': {'type': 'integer', 'minimum': 5, 'maximum': 100},
        'show_cover_images': {'type': 'boolean'},
        'default_search_type': {'type': 'string'},
        'show_reading_history': {'type': 'boolean'},
        'show_reviews': {'type': 'boolean'},
        'allow_recommendations': {'type': 'boolean'}
    }
})
def api_update_preferences():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
    
    data = request.get_json()
    try:
        user_prefs.update_preferences(**data)
        db.session.commit()
        return jsonify({'success': True, 'preferences': user_prefs.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/search-history', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['query'],
    'properties': {
        'query': {'type': 'string'}
    }
})
def api_add_search_history():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
    
    data = request.get_json()
    try:
        user_prefs.add_search_to_history(data['query'])
        db.session.commit()
        return jsonify({'success': True, 'search_history': user_prefs.search_history})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/saved-searches', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['name', 'params'],
    'properties': {
        'name': {'type': 'string'},
        'params': {'type': 'object'}
    }
})
def api_save_search():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
    
    data = request.get_json()
    try:
        user_prefs.save_search(data['name'], data['params'])
        db.session.commit()
        return jsonify({'success': True, 'saved_searches': user_prefs.saved_searches})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/saved-searches/<string:search_name>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_remove_saved_search(search_name):
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        return jsonify({'success': False, 'message': 'No preferences found'}), 404
    
    try:
        user_prefs.remove_saved_search(search_name)
        db.session.commit()
        return jsonify({'success': True, 'saved_searches': user_prefs.saved_searches})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/reading-goals', methods=['PUT'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'properties': {
        'books_per_year': {'type': 'integer', 'minimum': 0},
        'pages_per_day': {'type': 'integer', 'minimum': 0}
    }
})
def api_update_reading_goals():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
    
    data = request.get_json()
    try:
        user_prefs.update_reading_goals(
            books_per_year=data.get('books_per_year'),
            pages_per_day=data.get('pages_per_day')
        )
        db.session.commit()
        return jsonify({'success': True, 'reading_goals': user_prefs.reading_goals})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/preferred-categories', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['category'],
    'properties': {
        'category': {'type': 'string'}
    }
})
def api_add_preferred_category():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
    
    data = request.get_json()
    try:
        user_prefs.add_preferred_category(data['category'])
        db.session.commit()
        return jsonify({'success': True, 'preferred_categories': user_prefs.preferred_categories})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/preferred-categories/<string:category>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_remove_preferred_category(category):
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        return jsonify({'success': False, 'message': 'No preferences found'}), 404
    
    try:
        user_prefs.remove_preferred_category(category)
        db.session.commit()
        return jsonify({'success': True, 'preferred_categories': user_prefs.preferred_categories})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/preferred-authors', methods=['POST'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
@validate_json_schema({
    'type': 'object',
    'required': ['author_id'],
    'properties': {
        'author_id': {'type': 'integer'}
    }
})
def api_add_preferred_author():
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        user_prefs = UserPreference.create_default(current_user.user_id)
        db.session.add(user_prefs)
    
    data = request.get_json()
    try:
        user_prefs.add_preferred_author(data['author_id'])
        db.session.commit()
        return jsonify({'success': True, 'preferred_authors': user_prefs.preferred_authors})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/preferences/preferred-authors/<int:author_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_remove_preferred_author(author_id):
    user_prefs = UserPreference.get_by_user_id(current_user.user_id)
    if not user_prefs:
        return jsonify({'success': False, 'message': 'No preferences found'}), 404
    
    try:
        user_prefs.remove_preferred_author(author_id)
        db.session.commit()
        return jsonify({'success': True, 'preferred_authors': user_prefs.preferred_authors})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

# Tag Management Routes
@app.route('/tags')
@login_required
def tag_list():
    """List all tags."""
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags/list.html', tags=tags)

@app.route('/tags/<int:tag_id>')
@login_required
def tag_detail(tag_id):
    """View tag details and associated books."""
    tag = Tag.query.get_or_404(tag_id)
    books = tag.books.order_by(Book.title).all()
    return render_template('tags/detail.html', tag=tag, books=books)

# Tag API Routes
@app.route('/api/tags', methods=['GET'])
@login_required
def get_tags():
    """Get all tags."""
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([tag.to_dict() for tag in tags])

@app.route('/api/tags', methods=['POST'])
@login_required
@permission_required('manage_tags')
def create_tag():
    """Create a new tag."""
    data = request.get_json()
    
    # Validate input
    schema = {
        'type': 'object',
        'required': ['name'],
        'properties': {
            'name': {'type': 'string', 'minLength': 1, 'maxLength': 50},
            'description': {'type': 'string'},
            'color': {'type': 'string', 'pattern': '^#[0-9a-fA-F]{6}$'}
        }
    }
    
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    # Check if tag already exists
    existing_tag = Tag.get_by_name(data['name'])
    if existing_tag:
        return jsonify({'error': 'Tag already exists'}), 409
    
    # Create new tag
    tag = Tag(
        name=data['name'],
        description=data.get('description'),
        color=data.get('color', '#6c757d'),
        created_by=current_user.user_id
    )
    
    try:
        db.session.add(tag)
        db.session.commit()
        return jsonify(tag.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags/<int:tag_id>', methods=['PUT'])
@login_required
@permission_required('manage_tags')
def update_tag(tag_id):
    """Update a tag."""
    tag = Tag.query.get_or_404(tag_id)
    data = request.get_json()
    
    # Validate input
    schema = {
        'type': 'object',
        'properties': {
            'name': {'type': 'string', 'minLength': 1, 'maxLength': 50},
            'description': {'type': 'string'},
            'color': {'type': 'string', 'pattern': '^#[0-9a-fA-F]{6}$'}
        }
    }
    
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    # Check if new name conflicts with existing tag
    if 'name' in data and data['name'] != tag.name:
        existing_tag = Tag.get_by_name(data['name'])
        if existing_tag:
            return jsonify({'error': 'Tag name already exists'}), 409
    
    try:
        tag.update(**data)
        db.session.commit()
        return jsonify(tag.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags/<int:tag_id>', methods=['DELETE'])
@login_required
@permission_required('manage_tags')
def delete_tag(tag_id):
    """Delete a tag."""
    tag = Tag.query.get_or_404(tag_id)
    
    try:
        tag.delete()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Book Tag API Routes
@app.route('/api/books/<int:book_id>/tags', methods=['GET'])
@login_required
def get_book_tags(book_id):
    """Get all tags for a book."""
    book = Book.query.get_or_404(book_id)
    return jsonify([tag.to_dict() for tag in book.tags])

@app.route('/api/books/<int:book_id>/tags', methods=['POST'])
@login_required
@permission_required('manage_tags')
def add_book_tag(book_id):
    """Add a tag to a book."""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()
    
    # Validate input
    schema = {
        'type': 'object',
        'required': ['tag_id'],
        'properties': {
            'tag_id': {'type': 'integer'}
        }
    }
    
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    tag = Tag.query.get_or_404(data['tag_id'])
    
    try:
        book_tag = BookTag.add_tag_to_book(book_id, tag.tag_id, current_user.user_id)
        return jsonify(book_tag.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/books/<int:book_id>/tags/<int:tag_id>', methods=['DELETE'])
@login_required
@permission_required('manage_tags')
def remove_book_tag(book_id, tag_id):
    """Remove a tag from a book."""
    book = Book.query.get_or_404(book_id)
    tag = Tag.query.get_or_404(tag_id)
    
    try:
        if BookTag.remove_tag_from_book(book_id, tag_id):
            return '', 204
        return jsonify({'error': 'Tag not associated with book'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Fine Management Routes
@app.route('/fines')
@login_required
def fine_list():
    """List all fines."""
    fines = Fine.query.order_by(Fine.created_at.desc()).all()
    return render_template('fines/list.html', fines=fines)

@app.route('/fines/<int:fine_id>')
@login_required
def fine_detail(fine_id):
    """View fine details."""
    fine = Fine.query.get_or_404(fine_id)
    return render_template('fines/detail.html', fine=fine)

# Fine API Routes
@app.route('/api/fines', methods=['GET'])
@login_required
def get_fines():
    """Get all fines."""
    fines = Fine.query.order_by(Fine.created_at.desc()).all()
    return jsonify([fine.to_dict() for fine in fines])

@app.route('/api/fines/<int:fine_id>', methods=['GET'])
@login_required
def get_fine(fine_id):
    """Get fine details."""
    fine = Fine.query.get_or_404(fine_id)
    return jsonify(fine.to_dict())

@app.route('/api/fines/<int:fine_id>/pay', methods=['POST'])
@login_required
def pay_fine(fine_id):
    """Pay a fine."""
    fine = Fine.query.get_or_404(fine_id)
    
    if fine.is_paid:
        return jsonify({'error': 'Fine is already paid'}), 400
    
    data = request.get_json()
    schema = {
        'type': 'object',
        'properties': {
            'payment_method': {'type': 'string', 'enum': ['cash', 'credit_card', 'debit_card', 'bank_transfer']},
            'payment_reference': {'type': 'string'},
            'notes': {'type': 'string'}
        },
        'required': ['payment_method']
    }
    
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        fine.pay(
            payment_method=data['payment_method'],
            payment_reference=data.get('payment_reference'),
            notes=data.get('notes')
        )
        db.session.commit()
        return jsonify(fine.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/fines/<int:fine_id>/waive', methods=['POST'])
@login_required
def waive_fine(fine_id):
    """Waive a fine."""
    fine = Fine.query.get_or_404(fine_id)
    
    if fine.is_paid:
        return jsonify({'error': 'Fine is already paid'}), 400
    
    data = request.get_json()
    schema = {
        'type': 'object',
        'properties': {
            'notes': {'type': 'string'}
        },
        'required': ['notes']
    }
    
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        fine.waive(notes=data['notes'])
        db.session.commit()
        return jsonify(fine.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/borrowings/<int:borrowing_id>/fines', methods=['GET'])
@login_required
@permission_required('manage_fines')
def get_borrowing_fines(borrowing_id):
    """Get all fines for a borrowing."""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    return jsonify([fine.to_dict() for fine in borrowing.fines])

@app.route('/api/borrowings/<int:borrowing_id>/fines', methods=['POST'])
@login_required
@permission_required('manage_fines')
def create_borrowing_fine(borrowing_id):
    """Create a fine for a borrowing."""
    borrowing = Borrowing.query.get_or_404(borrowing_id)
    data = request.get_json()
    
    # Validate input
    schema = {
        'type': 'object',
        'properties': {
            'notes': {'type': 'string'}
        }
    }
    
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    try:
        fine = Fine.create_for_borrowing(borrowing, notes=data.get('notes'))
        if fine:
            return jsonify(fine.to_dict()), 201
        return jsonify({'error': 'No fine amount calculated'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Audit Log Routes
@app.route('/audit-logs')
@login_required
@permission_required('view_audit_logs')
def audit_log_list():
    """List audit logs with filtering."""
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AuditLog.query
    
    if action:
        query = query.filter_by(action=action)
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    if start_date:
        query = query.filter(AuditLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(AuditLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return render_template('audit/list.html', logs=logs)

@app.route('/api/audit-logs/<int:log_id>')
@login_required
@permission_required('view_audit_logs')
def get_audit_log(log_id):
    """Get audit log details."""
    log = AuditLog.query.get_or_404(log_id)
    return jsonify(log.to_dict())

@app.route('/api/audit-logs')
@login_required
@permission_required('view_audit_logs')
def get_audit_logs():
    """Get filtered audit logs."""
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = AuditLog.query
    
    if action:
        query = query.filter_by(action=action)
    if resource_type:
        query = query.filter_by(resource_type=resource_type)
    if start_date:
        query = query.filter(AuditLog.created_at >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(AuditLog.created_at <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    logs = query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs])

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)

