"""
Models package for the Library Management System.
This module provides access to all database models and handles their initialization.
"""

from typing import List, Type
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# Core models - import User first to ensure users table is created before foreign key references
from models.user import User
from models.book import Book
from models.author import Author
from models.publisher import Publisher
from models.category import Category
from models.book_copy import BookCopy
from models.borrowing import Borrowing

# Membership related models
from models.membership_type import MembershipType
from models.user_membership import UserMembership

# Enhanced functionality models
from models.enhanced_book import EnhancedBook
from models.enhanced_borrowing import EnhancedBorrowing
from models.library_event import LibraryEvent  # Import from library_event.py only
from models.event_registration import EventRegistration

# Financial and review models
from models.fine import Fine
from models.review import Review
from models.reservation import Reservation

# Tagging and notification models
from models.tag import Tag
from models.book_tag import BookTag
from models.notification import Notification

# System models
from models.audit_log import AuditLog
from models.user_preference import UserPreference
from models.reports import Reports
from models.branch import Branch

def init_models() -> None:
    """
    Initialize all models and create database tables.
    This function should be called after the Flask app is created.
    """
    # Create all tables in the correct order
    db.create_all()

# Export all models
__all__ = [
    'User',
    'Book',
    'Author',
    'Publisher',
    'Category',
    'BookCopy',
    'Borrowing',
    'MembershipType',
    'UserMembership',
    'EnhancedBook',
    'EnhancedBorrowing',
    'LibraryEvent',
    'EventRegistration',
    'Fine',
    'Review',
    'Reservation',
    'Tag',
    'BookTag',
    'Notification',
    'AuditLog',
    'UserPreference',
    'Reports',
    'Branch',
] 