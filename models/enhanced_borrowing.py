"""
Enhanced Borrowing model for the Library Management System.
Provides advanced borrowing management functionality with detailed information.
"""

from models import db
from datetime import UTC, datetime, timedelta, date
from sqlalchemy import func, and_, or_, desc, case
from sqlalchemy.orm import joinedload
from typing import List, Dict, Optional, Tuple

class EnhancedBorrowing:
    """Class providing enhanced borrowing management functionality."""

    @staticmethod
    def borrow_book_copy(user_id: int, copy_id: int, custom_duration: Optional[int] = None) -> Tuple[bool, str]:
        """
        Borrow a specific book copy for a user, enforcing membership and borrowing rules.
        
        Args:
            user_id (int): ID of the user borrowing the book
            copy_id (int): ID of the book copy
            custom_duration (int, optional): Custom loan duration in days
        Returns:
            Tuple[bool, str]: (success, message)
        """
        from models.user_membership import UserMembership
        from models.membership_type import MembershipType
        from models.book import Book
        from models.borrowing import Borrowing
        from models.fine import Fine
        from models.book_copy import BookCopy

        # Get user's active membership
        membership = (
            db.session.query(UserMembership, MembershipType)
            .join(MembershipType, UserMembership.membership_type_id == MembershipType.membership_type_id)
            .filter(UserMembership.user_id == user_id, UserMembership.is_active == True)
            .order_by(UserMembership.end_date.desc())
            .first()
        )
        if not membership:
            return False, "No valid membership found"
        max_books_allowed = membership[1].max_books_allowed
        loan_duration_days = membership[1].loan_duration_days

        # Check current borrowing count
        current_count = (
            db.session.query(func.count(Borrowing.borrowing_id))
            .filter(Borrowing.user_id == user_id, Borrowing.status.in_(['borrowed', 'overdue']))
            .scalar()
        )
        if current_count >= max_books_allowed:
            return False, f"Maximum borrowing limit ({max_books_allowed}) reached"

        # Check if copy is available
        copy = db.session.query(BookCopy).filter_by(copy_id=copy_id).first()
        if not copy:
            return False, "Book copy not found"
        if not copy.is_available:
            return False, "Book copy is not available"

        # Calculate due date
        loan_duration = custom_duration or loan_duration_days
        due_date = date.today() + timedelta(days=loan_duration)

        # Create borrowing record
        borrowing = Borrowing(
            user_id=user_id,
            book_id=copy.book_id,
            copy_id=copy_id,
            borrow_date=date.today(),
            due_date=due_date,
            status='borrowed'
        )
        db.session.add(borrowing)

        # Update copy availability
        copy.is_available = False

        # Update book availability count
        book = db.session.query(Book).filter_by(book_id=copy.book_id).first()
        if book:
            book.copies_available = book.copies_available - 1

        try:
            db.session.commit()
            return True, f"Book '{book.title if book else ''}' borrowed successfully. Due date: {due_date}"
        except Exception as e:
            db.session.rollback()
            return False, f"Error borrowing book: {str(e)}"

    @staticmethod
    def get_user_borrowings_detailed(user_id: int) -> List[Dict]:
        """
        Get detailed borrowing information for a user, including book, copy, branch, author, and fine details.
        
        Args:
            user_id (int): ID of the user
        Returns:
            List[Dict]: List of dictionaries with borrowing details
        """
        from models.borrowing import Borrowing
        from models.book import Book
        from models.book_copy import BookCopy
        from models.library import LibraryBranch
        from models.book_author import BookAuthor
        from models.author import Author
        from models.fine import Fine

        # Query borrowings with joins
        borrowings = (
            db.session.query(Borrowing)
            .options(
                joinedload(Borrowing.book),
                joinedload(Borrowing.copy).joinedload(BookCopy.branch),
                joinedload(Borrowing.book).joinedload(Book.authors),
                joinedload(Borrowing.fines)
            )
            .filter(Borrowing.user_id == user_id)
            .order_by(
                case([(Borrowing.status.in_(['borrowed', 'overdue']), 0)], else_=1),
                Borrowing.borrow_date.desc()
            )
            .all()
        )
        result = []
        for b in borrowings:
            # Get main author
            main_author = None
            for ba in b.book.authors:
                if hasattr(ba, 'role') and ba.role == 'author':
                    main_author = f"{ba.first_name} {ba.last_name}"
                    break
            if not main_author and b.book.authors:
                main_author = f"{b.book.authors[0].first_name} {b.book.authors[0].last_name}"
            # Calculate days overdue
            days_overdue = 0
            if b.status in ('borrowed', 'overdue') and b.due_date and b.due_date < date.today():
                days_overdue = (date.today() - b.due_date).days
            # Calculate fines
            total_fines = sum(f.amount for f in b.fines)
            unpaid_fines = sum(f.amount for f in b.fines if not f.is_paid)
            result.append({
                'borrowing_id': b.borrowing_id,
                'borrow_date': b.borrow_date.isoformat() if b.borrow_date else None,
                'due_date': b.due_date.isoformat() if b.due_date else None,
                'return_date': b.return_date.isoformat() if b.return_date else None,
                'status': b.status,
                'title': b.book.title if b.book else None,
                'isbn': b.book.isbn if b.book else None,
                'author': main_author,
                'barcode': b.copy.barcode if b.copy else None,
                'condition_status': b.copy.condition_status if b.copy else None,
                'branch_name': b.copy.branch.name if b.copy and b.copy.branch else None,
                'days_overdue': days_overdue,
                'total_fines': total_fines,
                'unpaid_fines': unpaid_fines
            })
        return result