from datetime import datetime
from flask_mysqldb import MySQL
from app import mysql

class Notification:
    @staticmethod
    def create(user_id, message, notification_type, related_id=None):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO notifications (user_id, message, notification_type, related_id)
            VALUES (%s, %s, %s, %s)
        """, (user_id, message, notification_type, related_id))
        mysql.connection.commit()
        notification_id = cursor.lastrowid
        cursor.close()
        return notification_id
    
    @staticmethod
    def get_user_notifications(user_id, limit=10, unread_only=False):
        cursor = mysql.connection.cursor(dictionary=True)
        query = """
            SELECT notification_id, message, notification_type, related_id, 
                   created_at, is_read
            FROM notifications
            WHERE user_id = %s
        """
        
        if unread_only:
            query += " AND is_read = 0"
            
        query += " ORDER BY created_at DESC LIMIT %s"
        
        cursor.execute(query, (user_id, limit))
        notifications = cursor.fetchall()
        cursor.close()
        return notifications
    
    @staticmethod
    def mark_as_read(notification_id):
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE notifications SET is_read = 1
            WHERE notification_id = %s
        """, (notification_id,))
        mysql.connection.commit()
        cursor.close()
        return True
    
    @staticmethod
    def create_due_date_notifications():
        """Create notifications for books due tomorrow"""
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT b.borrowing_id, b.user_id, b.due_date, bk.title
            FROM borrowings b
            JOIN books bk ON b.book_id = bk.book_id
            WHERE b.status = 'borrowed' 
            AND b.due_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY)
        """)
        
        due_tomorrow = cursor.fetchall()
        for borrowing in due_tomorrow:
            message = f"Your book '{borrowing['title']}' is due tomorrow."
            Notification.create(
                borrowing['user_id'], 
                message, 
                'due_date_reminder', 
                borrowing['borrowing_id']
            )
        
        cursor.close()
        return len(due_tomorrow)