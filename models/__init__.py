"""
Initialize all models for the Library Management System.
Import order is important for foreign key relationships.
"""

from extensions import db

# Base models (no foreign keys)
from models.user import User
from models.publisher import Publisher
from models.category import Category
from models.author import Author
from models.tag import Tag, BookTag

# Models with foreign keys to base models
from models.book import Book
from models.book_copy import BookCopy
from models.book_author import BookAuthor
from models.book_review import BookReview
from models.membership import MembershipType, UserMembership

# Models with foreign keys to previous models
from models.borrowing import Borrowing, Fine, FinePayment, Reservation
from models.library_event import LibraryEvent
from models.event_registration import EventRegistration
from models.notification import Notification, AuditLog, UserPreference
from .library_branch import LibraryBranch

def init_models():
    """Initialize all models and create database tables."""
    # This function is a placeholder - tables are created by db.create_all()
    # when called from the application factory
    pass

# Export all models
__all__ = [
    'User',
    'Book',
    'Author',
    'Publisher',
    'Category',
    'BookAuthor',
    'BookReview',
    'MembershipType',
    'UserMembership',
    'Borrowing',
    'Fine',
    'FinePayment',
    'Reservation',
    'LibraryEvent',
    'Notification',
    'AuditLog',
    'UserPreference',
] 