from app import app, db
from models.user import User, Permission, UserPermission
from models.book import Book, Publisher, Category, Author, BookAuthor, BookCopy, BookReview
from models.borrowing import Borrowing, FinePayment, Reservation
from models.library import LibraryBranch, MembershipType, UserMembership, LibraryEvent, EventRegistration
from models.notification import Notification, AuditLog, UserPreference
from datetime import datetime, timedelta
import os

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()

        # Create default permissions
        permissions = [
            Permission(name='admin', description='Administrator access'),
            Permission(name='librarian', description='Librarian access'),
            Permission(name='member', description='Regular member access')
        ]
        for permission in permissions:
            if not Permission.query.filter_by(name=permission.name).first():
                db.session.add(permission)
        db.session.commit()

        # Create default admin user
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@library.com',
                full_name='System Administrator',
                role='admin'
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()

            # Assign admin permission
            admin_permission = Permission.query.filter_by(name='admin').first()
            user_permission = UserPermission(
                user_id=admin.user_id,
                permission_id=admin_permission.permission_id
            )
            db.session.add(user_permission)
            db.session.commit()

        # Create default membership types
        membership_types = [
            MembershipType(
                name='Basic',
                description='Basic membership with standard borrowing privileges',
                max_books=5,
                loan_period=14,
                renewal_period=365,
                fee=0
            ),
            MembershipType(
                name='Premium',
                description='Premium membership with extended borrowing privileges',
                max_books=10,
                loan_period=21,
                renewal_period=365,
                fee=50
            )
        ]
        for membership_type in membership_types:
            if not MembershipType.query.filter_by(name=membership_type.name).first():
                db.session.add(membership_type)
        db.session.commit()

        # Create default categories
        categories = [
            Category(name='Fiction', description='Fictional works'),
            Category(name='Non-Fiction', description='Non-fictional works'),
            Category(name='Science', description='Scientific works'),
            Category(name='History', description='Historical works'),
            Category(name='Biography', description='Biographical works')
        ]
        for category in categories:
            if not Category.query.filter_by(name=category.name).first():
                db.session.add(category)
        db.session.commit()

        # Create default library branch
        main_branch = LibraryBranch.query.filter_by(name='Main Branch').first()
        if not main_branch:
            main_branch = LibraryBranch(
                name='Main Branch',
                address='123 Library Street, City, Country',
                phone='+1234567890',
                email='main@library.com',
                opening_hours='Mon-Fri: 9:00-18:00, Sat-Sun: 10:00-16:00',
                manager_id=admin.user_id
            )
            db.session.add(main_branch)
            db.session.commit()

        print("Database initialized successfully!")

if __name__ == '__main__':
    init_database() 