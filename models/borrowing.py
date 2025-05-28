# Borrowing model in models/borrowing.py
from datetime import datetime, timedelta

class Borrowing:
    @staticmethod
    def borrow_book(user_id, book_id, days=14):
        cursor = mysql.connection.cursor()
        
        # Check if book is available
        cursor.execute("SELECT copies_available FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        
        if not book or book[0] <= 0:
            cursor.close()
            return False, "Book not available for borrowing"
        
        # Create borrowing record
        borrow_date = datetime.now().date()
        due_date = borrow_date + timedelta(days=days)
        
        cursor.execute(
            "INSERT INTO borrowings (user_id, book_id, borrow_date, due_date, status) VALUES (%s, %s, %s, %s, 'borrowed')",
            (user_id, book_id, borrow_date, due_date)
        )
        
        # Update book availability
        cursor.execute(
            "UPDATE books SET copies_available = copies_available - 1 WHERE book_id = %s",
            (book_id,)
        )
        
        mysql.connection.commit()
        cursor.close()
        return True, f"Book borrowed successfully. Due date: {due_date}"
    
    @staticmethod
    def return_book(borrowing_id):
        cursor = mysql.connection.cursor()
        
        # Check if borrowing exists and is not already returned
        cursor.execute("""
            SELECT b.borrowing_id, b.book_id, b.due_date, b.status 
            FROM borrowings b 
            WHERE b.borrowing_id = %s AND b.status = 'borrowed'
        """, (borrowing_id,))
        
        borrowing = cursor.fetchone()
        if not borrowing:
            cursor.close()
            return False, "Borrowing record not found or already returned"
        
        book_id = borrowing[1]
        due_date = borrowing[2]
        return_date = datetime.now().date()
        
        # Calculate fine if overdue
        fine = 0.0
        if return_date > due_date:
            days_overdue = (return_date - due_date).days
            fine = days_overdue * 0.50  # $0.50 per day overdue
        
        # Update borrowing record
        cursor.execute(
            "UPDATE borrowings SET return_date = %s, status = 'returned', fine = %s WHERE borrowing_id = %s",
            (return_date, fine, borrowing_id)
        )
        
        # Update book availability
        cursor.execute(
            "UPDATE books SET copies_available = copies_available + 1 WHERE book_id = %s",
            (book_id,)
        )
        
        mysql.connection.commit()
        cursor.close()
        
        message = f"Book returned successfully."
        if fine > 0:
            message += f" Fine charged: ${fine:.2f}"
        
        return True, message
    
    @staticmethod
    def get_user_borrowings(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT b.borrowing_id, b.borrow_date, b.due_date, b.return_date, b.status, b.fine,
                   bk.book_id, bk.title, bk.author
            FROM borrowings b
            JOIN books bk ON b.book_id = bk.book_id
            WHERE b.user_id = %s
            ORDER BY 
                CASE 
                    WHEN b.status = 'borrowed' THEN 0
                    WHEN b.status = 'overdue' THEN 1
                    ELSE 2
                END,
                b.borrow_date DESC
        """, (user_id,))
        borrowings = cursor.fetchall()
        cursor.close()
        return borrowings
    
    @staticmethod
    def update_overdue_status():
        cursor = mysql.connection.cursor()
        today = datetime.now().date()
        
        cursor.execute(
            "UPDATE borrowings SET status = 'overdue' WHERE due_date < %s AND status = 'borrowed'",
            (today,)
        )
        
        mysql.connection.commit()
        cursor.close()