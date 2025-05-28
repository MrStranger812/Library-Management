from flask_mysqldb import MySQL
from app import mysql

class Reports:
    @staticmethod
    def get_overdue_books():
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.borrowing_id, b.borrow_date, b.due_date, 
                   u.user_id, u.username, u.full_name, u.email,
                   bk.book_id, bk.title, bk.isbn, bk.author
            FROM borrowings b
            JOIN users u ON b.user_id = u.user_id
            JOIN books bk ON b.book_id = bk.book_id
            WHERE b.status = 'borrowed' AND b.due_date < CURDATE()
            ORDER BY b.due_date ASC
        """)
        overdue_books = cursor.fetchall()
        cursor.close()
        return overdue_books
    
    @staticmethod
    def get_popular_books(limit=10):
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.book_id, b.title, b.author, b.category, 
                   COUNT(br.borrowing_id) as borrow_count
            FROM books b
            JOIN borrowings br ON b.book_id = br.book_id
            GROUP BY b.book_id
            ORDER BY borrow_count DESC
            LIMIT %s
        """, (limit,))
        popular_books = cursor.fetchall()
        cursor.close()
        return popular_books
    
    @staticmethod
    def get_user_activity(days=30):
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.user_id, u.username, u.full_name, u.role,
                   COUNT(br.borrowing_id) as borrow_count,
                   SUM(CASE WHEN br.status = 'overdue' THEN 1 ELSE 0 END) as overdue_count,
                   SUM(br.fine) as total_fines
            FROM users u
            LEFT JOIN borrowings br ON u.user_id = br.user_id AND br.borrow_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY u.user_id
            ORDER BY borrow_count DESC
        """, (days,))
        user_activity = cursor.fetchall()
        cursor.close()
        return user_activity