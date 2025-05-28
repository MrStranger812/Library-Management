from datetime import datetime
from flask_mysqldb import MySQL
from app import mysql

class Review:
    @staticmethod
    def add_review(user_id, book_id, rating, comment):
        cursor = mysql.connection.cursor()
        
        # Check if user has borrowed this book
        cursor.execute("""
            SELECT 1 FROM borrowings 
            WHERE user_id = %s AND book_id = %s
        """, (user_id, book_id))
        
        if not cursor.fetchone():
            cursor.close()
            return False, "You can only review books you have borrowed"
        
        # Check if user already reviewed this book
        cursor.execute("""
            SELECT review_id FROM reviews 
            WHERE user_id = %s AND book_id = %s
        """, (user_id, book_id))
        
        existing_review = cursor.fetchone()
        if existing_review:
            # Update existing review
            cursor.execute("""
                UPDATE reviews 
                SET rating = %s, comment = %s, updated_at = NOW() 
                WHERE review_id = %s
            """, (rating, comment, existing_review[0]))
            message = "Review updated successfully"
        else:
            # Create new review
            cursor.execute("""
                INSERT INTO reviews (user_id, book_id, rating, comment) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, book_id, rating, comment))
            message = "Review added successfully"
        
        mysql.connection.commit()
        cursor.close()
        return True, message
    
    @staticmethod
    def get_book_reviews(book_id):
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.review_id, r.rating, r.comment, r.created_at, 
                   u.username, u.full_name
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.book_id = %s
            ORDER BY r.created_at DESC
        """, (book_id,))
        reviews = cursor.fetchall()
        cursor.close()
        return reviews