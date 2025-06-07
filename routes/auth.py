from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models.user import User
from utils.security import Security

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
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

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index')) 