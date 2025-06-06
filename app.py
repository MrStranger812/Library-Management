from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from config import Config
import os
from extensions import mysql, bcrypt, login_manager
from utils.security import Security
from utils.middleware import security_headers, validate_request, require_https, validate_json_schema, log_request, handle_cors

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
mysql.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models
from models.user import User
from models.book import Book
from models.borrowing import Borrowing
from models.user import Permission

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
    'required': ['isbn', 'title', 'author', 'category'],
    'properties': {
        'isbn': {'type': 'string'},
        'title': {'type': 'string'},
        'author': {'type': 'string'},
        'category': {'type': 'string'},
        'publicationYear': {'type': 'integer'},
        'copies': {'type': 'integer', 'minimum': 1}
    }
})
def api_add_book():
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    try:
        book_id = Book.create(
            data['isbn'],
            data['title'],
            data['author'],
            data['category'],
            data.get('publicationYear'),
            int(data.get('copies', 1))
        )
        return jsonify({'success': True, 'book_id': book_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/books', methods=['GET'])
def api_get_books():
    query = request.args.get('q', '')
    if query:
        books = Book.search(query)
    else:
        books = Book.get_all()
    
    # Convert books to JSON-friendly format
    books_list = []
    for book in books:
        books_list.append({
            'book_id': book[0],
            'isbn': book[1],
            'title': book[2],
            'author': book[3],
            'category': book[4],
            'publication_year': book[5],
            'copies_available': book[6],
            'total_copies': book[7]
        })
    
    return jsonify(books_list)

@app.route('/api/books/<int:book_id>', methods=['GET'])
def api_get_book(book_id):
    book = Book.get_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    
    book_data = {
        'book_id': book[0],
        'isbn': book[1],
        'title': book[2],
        'author': book[3],
        'category': book[4],
        'publication_year': book[5],
        'copies_available': book[6],
        'total_copies': book[7]
    }
    
    return jsonify(book_data)

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_delete_book(book_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    try:
        Book.delete(book_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/users', methods=['GET'])
@login_required
@Security.require_api_key()
@validate_request()
@security_headers()
def api_get_users():
    if not current_user.has_permission('manage_users'):
        return jsonify({'error': 'Permission denied'}), 403
    
    users = User.get_all()
    return jsonify(users)

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
    
    # Validate password
    is_valid, message = Security.validate_password(data['password'])
    if not is_valid:
        return jsonify({'success': False, 'message': message}), 400
    
    try:
        user_id = User.create(
            data['username'],
            data['password'],
            data['full_name'],
            data['email'],
            data['role']
        )
        return jsonify({'success': True, 'user_id': user_id})
    except Exception as e:
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
    if not current_user.has_permission('borrow_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    book_id = data['book_id']
    days = data.get('days', 14)
    
    success, message = Borrowing.borrow_book(current_user.id, book_id, days)
    
    return jsonify({
        'success': success,
        'message': message
    })

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
    if not current_user.has_permission('return_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    borrowing_id = data['borrowing_id']
    
    success, message = Borrowing.return_book(borrowing_id)
    
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/borrowings/user', methods=['GET'])
@login_required
def api_get_user_borrowings():
    user_id = request.args.get('user_id')
    
    # If requesting other user's borrowings, check permission
    if user_id and int(user_id) != current_user.id and not current_user.has_permission('manage_users'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # If no user_id specified, use current user
    if not user_id:
        user_id = current_user.id
    
    borrowings = Borrowing.get_user_borrowings(user_id)
    
    # Convert borrowings to JSON-friendly format
    borrowings_list = []
    for borrowing in borrowings:
        borrowings_list.append({
            'borrowing_id': borrowing[0],
            'book_id': borrowing[1],
            'user_id': borrowing[2],
            'borrow_date': borrowing[3],
            'return_date': borrowing[4],
            'returned': borrowing[5]
        })
    
    return jsonify(borrowings_list)

@app.route('/api/permissions', methods=['GET'])
@login_required
def api_get_permissions():
    if not current_user.has_permission('manage_permissions'):
        return jsonify({'error': 'Permission denied'}), 403
    
    permissions = Permission.get_all()
    
    # Convert to JSON-friendly format
    permissions_list = []
    for permission in permissions:
        permissions_list.append({
            'permission_id': permission[0],
            'name': permission[1],
            'description': permission[2] if len(permission) > 2 else ''
        })
    
    return jsonify(permissions_list)

@app.route('/api/permissions/grant', methods=['POST'])
@login_required
def api_grant_permission():
    if not current_user.has_permission('manage_permissions'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    permission_id = data.get('permission_id')
    
    success, message = Permission.grant(user_id, permission_id, current_user.id)
    
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/permissions/revoke', methods=['POST'])
@login_required
def api_revoke_permission():
    if not current_user.has_permission('manage_permissions'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    permission_id = data.get('permission_id')
    
    success, message = Permission.revoke(user_id, permission_id)
    
    return jsonify({
        'success': success,
        'message': message
    })

if __name__ == '__main__':
    app.run(debug=Config.DEBUG)

