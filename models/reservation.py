from datetime import datetime
from flask_mysqldb import MySQL
from app import mysql

class Reservation:
    @staticmethod
    def reserve_book(user_id, book_id):
        cursor = mysql.connection.cursor()
        
        # Check if book exists and is unavailable
        cursor.execute("SELECT copies_available FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        
        if not book:
            cursor.close()
            return False, "Book not found"
        
        if book[0] > 0:
            cursor.close()
            return False, "Book is available for borrowing, no need to reserve"
        
        # Check if user already has a reservation for this book
        cursor.execute("""
            SELECT 1 FROM reservations 
            WHERE user_id = %s AND book_id = %s AND status = 'pending'
        """, (user_id, book_id))
        
        if cursor.fetchone():
            cursor.close()
            return False, "You already have a pending reservation for this book"
        
        # Create reservation
        reservation_date = datetime.now().date()
        
        cursor.execute(
            "INSERT INTO reservations (user_id, book_id, reservation_date, status) VALUES (%s, %s, %s, 'pending')",
            (user_id, book_id, reservation_date)
        )
        
        mysql.connection.commit()
        cursor.close()
        return True, "Book reserved successfully. You will be notified when it becomes available."