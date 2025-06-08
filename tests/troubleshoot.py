#!/usr/bin/env python
"""
Troubleshooting script to identify common issues in the Library Management System.
Run with: python troubleshoot.py
"""

import sys
import os
import importlib

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def check_imports():
    """Check if all required modules can be imported."""
    print("🔍 Checking imports...")
    
    modules_to_check = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'Flask-SQLAlchemy'),
        ('flask_login', 'Flask-Login'),
        ('flask_bcrypt', 'Flask-Bcrypt'),
        ('pymysql', 'PyMySQL'),
        ('extensions', 'Extensions module'),
        ('models.user', 'User model'),
        ('models.book', 'Book model'),
        ('models.borrowing', 'Borrowing model'),
    ]
    
    issues = []
    
    for module_name, display_name in modules_to_check:
        try:
            importlib.import_module(module_name)
            print(f"✅ {display_name}")
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
            issues.append(display_name)
    
    return len(issues) == 0

def check_database_schema():
    """Check if database schema matches models."""
    print("\n🗄️  Checking database schema...")
    
    try:
        from app import get_app
        from extensions import db
        
        app = get_app()
        
        with app.app_context():
            # Get all tables from database
            inspector = db.inspect(db.engine)
            db_tables = inspector.get_table_names()
            
            # Expected tables from schema.sql
            expected_tables = [
                'users', 'books', 'borrowings', 'fines', 'notifications',
                'permissions', 'user_permissions', 'audit_logs', 'reservations',
                'book_reviews', 'publishers', 'categories', 'authors',
                'book_authors', 'book_copies', 'membership_types',
                'user_memberships', 'library_branches', 'library_events',
                'event_registrations', 'user_preferences', 'book_tags',
                'book_tag_assignments'
            ]
            
            missing_tables = []
            for table in expected_tables:
                if table in db_tables:
                    print(f"✅ Table: {table}")
                else:
                    print(f"❌ Table: {table} (missing)")
                    missing_tables.append(table)
            
            # Check for extra tables
            extra_tables = set(db_tables) - set(expected_tables)
            if extra_tables:
                print(f"\n⚠️  Extra tables found: {', '.join(extra_tables)}")
            
            return len(missing_tables) == 0
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def check_model_attributes():
    """Check if model attributes match database columns."""
    print("\n🔍 Checking model attributes...")
    
    try:
        from models.user import User
        from models.book import Book
        from models.borrowing import Borrowing
        
        # Check User model
        user_attrs = ['user_id', 'username', 'password', 'email', 'full_name', 'role']
        print("\nUser model:")
        for attr in user_attrs:
            if hasattr(User, attr):
                print(f"✅ {attr}")
            else:
                print(f"❌ {attr} (missing)")
        
        # Check Book model
        book_attrs = ['book_id', 'isbn', 'title', 'author', 'total_copies', 'copies_available']
        print("\nBook model:")
        for attr in book_attrs:
            if hasattr(Book, attr):
                print(f"✅ {attr}")
            else:
                print(f"❌ {attr} (missing)")
        
        # Check Borrowing model
        borrowing_attrs = ['borrowing_id', 'user_id', 'book_id', 'borrow_date', 'due_date', 'status']
        print("\nBorrowing model:")
        for attr in borrowing_attrs:
            if hasattr(Borrowing, attr):
                print(f"✅ {attr}")
            else:
                print(f"❌ {attr} (missing)")
        
        return True
        
    except Exception as e:
        print(f"❌ Model check failed: {e}")
        return False

def check_test_setup():
    """Check if test setup is correct."""
    print("\n🧪 Checking test setup...")
    
    # Check if test directories exist
    test_dirs = ['tests', 'tests/unit', 'tests/integration', 'tests/e2e', 'tests/fixtures']
    
    for dir_path in test_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory: {dir_path}")
        else:
            print(f"❌ Directory: {dir_path} (missing)")
    
    # Check if conftest.py exists
    if os.path.exists('tests/conftest.py'):
        print("✅ tests/conftest.py exists")
    else:
        print("❌ tests/conftest.py missing")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest installed (version {pytest.__version__})")
    except ImportError:
        print("❌ pytest not installed")
    
    return True

def suggest_fixes():
    """Suggest fixes for common issues."""
    print("\n💡 Suggested fixes:")
    print("-" * 40)
    
    suggestions = [
        "1. Install missing dependencies: pip install -r requirements.txt",
        "2. Create missing tables: python -c 'from app import app, db; app.app_context().push(); db.create_all()'",
        "3. Update model primary keys: Change .id to .user_id, .book_id, etc.",
        "4. Add helper methods to models or update tests to not use them",
        "5. Use correct password format: Test123! (uppercase, lowercase, digit, special char)",
        "6. Create parent records (Publisher, Category) before creating Books",
        "7. Use unique values for tests (generate random ISBNs, usernames)",
        "8. Check import paths - ensure they match your project structure"
    ]
    
    for suggestion in suggestions:
        print(suggestion)

def main():
    """Run all troubleshooting checks."""
    print("🔧 Library Management System - Troubleshooting")
    print("=" * 60)
    
    all_good = True
    
    # Run checks
    if not check_imports():
        all_good = False
    
    if not check_database_schema():
        all_good = False
    
    if not check_model_attributes():
        all_good = False
    
    if not check_test_setup():
        all_good = False
    
    # Show results
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All checks passed!")
    else:
        print("❌ Some issues found.")
        suggest_fixes()
    
    print("\n📝 Next steps:")
    print("1. Fix any issues identified above")
    print("2. Run the minimal test: pytest test_minimal.py -v")
    print("3. Gradually add more complex tests")

if __name__ == "__main__":
    main()