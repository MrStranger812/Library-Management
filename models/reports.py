"""
Reports model for the Library Management System.
Provides various reporting functionalities for library operations.
"""

from models import db
from datetime import UTC, datetime, timedelta
from sqlalchemy import func, case, desc, and_
from models.borrowing import Borrowing
from models.book import Book
from models.user import User

class Reports:
    """Class containing various reporting methods for the library system."""

    @staticmethod
    def get_overdue_books():
        """
        Get all overdue books with user and book details.
        
        Returns:
            list: List of dictionaries containing overdue book information.
        """
        return db.session.query(
            Borrowing,
            User,
            Book
        ).join(
            User, Borrowing.user_id == User.user_id
        ).join(
            Book, Borrowing.book_id == Book.book_id
        ).filter(
            Borrowing.status == 'borrowed',
            Borrowing.due_date < datetime.now(UTC).date()
        ).order_by(
            Borrowing.due_date.asc()
        ).all()

    @staticmethod
    def get_popular_books(limit=10, days=None):
        """
        Get the most popular books based on borrowing count.
        
        Args:
            limit (int): Maximum number of books to return.
            days (int, optional): Only count borrowings within this many days.
            
        Returns:
            list: List of dictionaries containing popular book information.
        """
        query = db.session.query(
            Book,
            func.count(Borrowing.borrowing_id).label('borrow_count')
        ).join(
            Borrowing, Book.book_id == Borrowing.book_id
        )
        
        if days:
            query = query.filter(
                Borrowing.borrow_date >= datetime.now(UTC).date() - timedelta(days=days)
            )
            
        return query.group_by(
            Book.book_id
        ).order_by(
            desc('borrow_count')
        ).limit(limit).all()

    @staticmethod
    def get_user_activity(days=30):
        """
        Get user activity statistics for the specified period.
        
        Args:
            days (int): Number of days to look back for activity.
            
        Returns:
            list: List of dictionaries containing user activity information.
        """
        return db.session.query(
            User,
            func.count(Borrowing.borrowing_id).label('borrow_count'),
            func.sum(case((Borrowing.status == 'overdue', 1), else_=0)).label('overdue_count'),
            func.sum(Borrowing.fine_amount).label('total_fines')
        ).outerjoin(
            Borrowing,
            and_(
                User.user_id == Borrowing.user_id,
                Borrowing.borrow_date >= datetime.now(UTC).date() - timedelta(days=days)
            )
        ).group_by(
            User.user_id
        ).order_by(
            desc('borrow_count')
        ).all()

    @staticmethod
    def get_branch_statistics(branch_id=None):
        """
        Get statistics for library branches.
        
        Args:
            branch_id (int, optional): Specific branch ID to get statistics for.
            
        Returns:
            list: List of dictionaries containing branch statistics.
        """
        from models.branch import Branch
        from models.book_copy import BookCopy
        
        query = db.session.query(
            Branch,
            func.count(BookCopy.copy_id).label('total_copies'),
            func.sum(case((BookCopy.is_available == True, 1), else_=0)).label('available_copies'),
            func.count(Borrowing.borrowing_id).label('active_borrowings')
        ).outerjoin(
            BookCopy, Branch.branch_id == BookCopy.branch_id
        ).outerjoin(
            Borrowing, BookCopy.copy_id == Borrowing.copy_id
        )
        
        if branch_id:
            query = query.filter(Branch.branch_id == branch_id)
            
        return query.group_by(
            Branch.branch_id
        ).all()

    @staticmethod
    def get_fine_statistics(days=30):
        """
        Get fine statistics for the specified period.
        
        Args:
            days (int): Number of days to look back for fines.
            
        Returns:
            dict: Dictionary containing fine statistics.
        """
        from models.fine import Fine
        
        return db.session.query(
            func.sum(Fine.amount).label('total_fines'),
            func.count(case((Fine.is_paid == True, 1))).label('paid_fines'),
            func.count(case((Fine.is_paid == False, 1))).label('unpaid_fines'),
            func.avg(Fine.amount).label('average_fine')
        ).filter(
            Fine.created_at >= datetime.now(UTC) - timedelta(days=days)
        ).first()

    @staticmethod
    def get_event_statistics(days=30):
        """
        Get event statistics for the specified period.
        
        Args:
            days (int): Number of days to look back for events.
            
        Returns:
            list: List of dictionaries containing event statistics.
        """
        from models.library_event import LibraryEvent
        from models.event_registration import EventRegistration
        
        return db.session.query(
            LibraryEvent,
            func.count(EventRegistration.registration_id).label('registration_count')
        ).outerjoin(
            EventRegistration,
            LibraryEvent.event_id == EventRegistration.event_id
        ).filter(
            LibraryEvent.event_date >= datetime.now(UTC).date() - timedelta(days=days)
        ).group_by(
            LibraryEvent.event_id
        ).order_by(
            LibraryEvent.event_date.desc()
        ).all()