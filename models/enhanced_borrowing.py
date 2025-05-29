from utils.db_manager import get_db_cursor, execute_query

class EnhancedBorrowing:
    @staticmethod
    def borrow_book_copy(user_id, copy_id, custom_duration=None):
        """Borrow a specific book copy"""
        with get_db_cursor() as cursor:
            # Get user's membership details
            membership_query = """
                SELECT mt.max_books_allowed, mt.loan_duration_days
                FROM user_memberships um
                JOIN membership_types mt ON um.membership_type_id = mt.membership_type_id
                WHERE um.user_id = %s AND um.is_active = TRUE
                ORDER BY um.end_date DESC LIMIT 1
            """
            cursor.execute(membership_query, (user_id,))
            membership = cursor.fetchone()
            
            if not membership:
                return False, "No valid membership found"
            
            # Check current borrowing count
            count_query = """
                SELECT COUNT(*) as count FROM borrowings 
                WHERE user_id = %s AND status IN ('borrowed', 'overdue')
            """
            cursor.execute(count_query, (user_id,))
            current_count = cursor.fetchone()[0]
            
            if current_count >= membership[0]:  # max_books_allowed
                return False, f"Maximum borrowing limit ({membership[0]}) reached"
            
            # Check if copy is available
            copy_query = """
                SELECT bc.book_id, bc.is_available, b.title
                FROM book_copies bc
                JOIN books b ON bc.book_id = b.book_id
                WHERE bc.copy_id = %s
            """
            cursor.execute(copy_query, (copy_id,))
            copy_info = cursor.fetchone()
            
            if not copy_info:
                return False, "Book copy not found"
            
            if not copy_info[1]:  # is_available
                return False, "Book copy is not available"
            
            # Calculate due date
            from datetime import date, timedelta
            loan_duration = custom_duration or membership[1]  # loan_duration_days
            due_date = date.today() + timedelta(days=loan_duration)
            
            # Create borrowing record
            borrow_query = """
                INSERT INTO borrowings (user_id, book_id, copy_id, borrow_date, due_date, status)
                VALUES (%s, %s, %s, CURDATE(), %s, 'borrowed')
            """
            cursor.execute(borrow_query, (user_id, copy_info[0], copy_id, due_date))
            borrowing_id = cursor.lastrowid
            
            # Update copy availability
            update_query = "UPDATE book_copies SET is_available = FALSE WHERE copy_id = %s"
            cursor.execute(update_query, (copy_id,))
            
            # Update book availability count
            update_book_query = """
                UPDATE books SET copies_available = copies_available - 1 
                WHERE book_id = %s
            """
            cursor.execute(update_book_query, (copy_info[0],))
            
            return True, f"Book '{copy_info[2]}' borrowed successfully. Due date: {due_date}"
    
    @staticmethod
    def get_user_borrowings_detailed(user_id):
        """Get detailed borrowing information for a user"""
        query = """
            SELECT 
                b.borrowing_id, b.borrow_date, b.due_date, b.return_date, b.status,
                bk.title, bk.isbn,
                CONCAT(a.first_name, ' ', a.last_name) as author,
                bc.barcode, bc.condition_status,
                br.name as branch_name,
                CASE 
                    WHEN b.status IN ('borrowed', 'overdue') AND b.due_date < CURDATE() 
                    THEN DATEDIFF(CURDATE(), b.due_date)
                    ELSE 0 
                END as days_overdue,
                COALESCE(SUM(f.amount), 0) as total_fines,
                COALESCE(SUM(CASE WHEN f.is_paid THEN 0 ELSE f.amount END), 0) as unpaid_fines
            FROM borrowings b
            JOIN books bk ON b.book_id = bk.book_id
            LEFT JOIN book_copies bc ON b.copy_id = bc.copy_id
            LEFT JOIN library_branches br ON bc.branch_id = br.branch_id
            LEFT JOIN book_authors ba ON bk.book_id = ba.book_id AND ba.role = 'author'
            LEFT JOIN authors a ON ba.author_id = a.author_id
            LEFT JOIN fines f ON b.borrowing_id = f.borrowing_id
            WHERE b.user_id = %s
            GROUP BY b.borrowing_id
            ORDER BY 
                CASE WHEN b.status IN ('borrowed', 'overdue') THEN 0 ELSE 1 END,
                b.borrow_date DESC
        """
        return execute_query(query, (user_id,), dictionary=True)