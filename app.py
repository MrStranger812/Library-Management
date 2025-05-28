from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_mysqldb import MySQL
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from config import Config
import os
from extensions import mysql, bcrypt, login_manager

app = Flask(__name__)
app.config.from_object(Config)


mysql.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

from models.user import User
from models.book import Book
from models.borrowing import Borrowing
from models.user import Permission

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']
        # Check if user already exists
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('register.html')
        # Create user with default role (e.g., 'user')
        User.create(username, password, full_name, email, 'user')
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# API Routes for Books
@app.route('/api/books', methods=['GET'])
@login_required
def get_books():
    # Code to fetch books
    pass

@app.route('/api/books', methods=['POST'])
@login_required
def add_book():
    # Check permission
    if not current_user.has_permission('manage_books'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Code to add a book
    pass

# Implement other routes for users, permissions, borrowing
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

@app.route('/api/books', methods=['POST'])
@login_required
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

@app.route('/api/books/<int:book_id>', methods=['PUT'])
@login_required
def api_update_book(book_id):
    if not current_user.has_permission('manage_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
    try:
        Book.update(
            book_id,
            data['title'],
            data['author'],
            data['category'],
            data.get('publicationYear'),
            int(data.get('copies_available', 1)),
            int(data.get('total_copies', 1))
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@login_required
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
def api_get_users():
    if not current_user.has_permission('manage_users'):
        return jsonify({'error': 'Permission denied'}), 403
    
    # Code to fetch users
    # Similar to get_books implementation
    
@app.route('/api/users', methods=['POST'])
@login_required
def api_add_user():
    if not current_user.has_permission('manage_users'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    
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
def api_borrow_book():
    if not current_user.has_permission('borrow_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    book_id = data.get('book_id')
    days = data.get('days', 14)
    
    success, message = Borrowing.borrow_book(current_user.id, book_id, days)
    
    return jsonify({
        'success': success,
        'message': message
    })

@app.route('/api/borrowings/return', methods=['POST'])
@login_required
def api_return_book():
    if not current_user.has_permission('return_books'):
        return jsonify({'success': False, 'message': 'Permission denied'}), 403
    
    data = request.get_json()
    borrowing_id = data.get('borrowing_id')
    
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
    app.run(debug=True)

