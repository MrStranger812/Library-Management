"""Models package for the Library Management System.

This package contains all the database models used in the application.
Models are imported in order to maintain foreign key relationships.
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Base models (no foreign keys)
from models.user import User
from models.book import Book
from models.library_branch import LibraryBranch
from models.membership import MembershipType, UserMembership
from models.tag import Tag, BookTag

# Models with foreign keys to base models
from models.borrowing import Borrowing, Reservation
from models.fine import Fine
from models.fine_payment import FinePayment
from models.library_event import LibraryEvent
from models.event_registration import EventRegistration
from models.notification import Notification, AuditLog, UserPreference

def init_models():
    """Initialize all models and create database tables."""
    # This function is a placeholder - tables are created by db.create_all()
    # when called from the application factory
    pass

# Export all models
__all__ = [
    'db',
    'User',
    'Book',
    'LibraryBranch',
    'MembershipType',
    'UserMembership',
    'Tag',
    'BookTag',
    'Borrowing',
    'Reservation',
    'Fine',
    'FinePayment',
    'LibraryEvent',
    'EventRegistration',
    'Notification',
    'AuditLog',
    'UserPreference'
] 