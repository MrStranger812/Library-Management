from utils.db_manager import execute_query
from datetime import datetime, timedelta

class Statistics:
    @staticmethod
    def get_dashboard_stats():
        """Get statistics for dashboard"""
        stats = {}
        
        # Total books
        query = "SELECT COUNT(*) as count FROM books"
        result = execute_query(query, dictionary=True, fetchall=False)
        stats['total_books'] = result['count'] if result else 0
        
        # Total users
        query = "SELECT COUNT(*) as count FROM users"
        result = execute_query(query, dictionary=True, fetchall=False)
        stats['total_users'] = result['count'] if result else 0
        
        # Active borrowings
        query = "SELECT COUNT(*) as count FROM borrowings WHERE status = 'borrowed'"
        result = execute_query(query, dictionary=True, fetchall=False)
        stats['active_borrowings'] = result['count'] if result else 0
        
        # Overdue borrowings
        query = "SELECT COUNT(*) as count FROM borrowings WHERE status = 'overdue'"
        result = execute_query(query, dictionary=True, fetchall=False)
        stats['overdue_borrowings'] = result['count'] if result else 0
        
        # Books by category
        query = """
            SELECT category, COUNT(*) as count 
            FROM books 
            GROUP BY category 
            ORDER BY count DESC
        """
        stats['books_by_category'] = execute_query(query, dictionary=True)
        
        # Recent borrowings
        query = """
            SELECT b.borrowing_id, b.borrow_date, b.due_date, b.status,
                   u.username, u.full_name,
                   bk.title, bk.author
            FROM borrowings b
            JOIN users u ON b.user_id = u.user_id
            JOIN books bk ON b.book_id = bk.book_id
            ORDER BY b.borrow_date DESC
            LIMIT 5
        """
        stats['recent_borrowings'] = execute_query(query, dictionary=True)
        
        return stats
    
    @staticmethod
    def get_borrowing_stats(period='month'):
        """
        Get borrowing statistics for a specific period
        
        Args:
            period: 'week', 'month', or 'year'
        
        Returns:
            Dictionary with borrowing statistics
        """
        stats = {}
        
        # Set date range based on period
        today = datetime.now().date()
        if period == 'week':
            start_date = today - timedelta(days=7)
            date_format = '%a'  # Day of week abbreviation
        elif period == 'month':
            start_date = today - timedelta(days=30)
            date_format = '%d'  # Day of month
        elif period == 'year':
            start_date = today - timedelta(days=365)
            date_format = '%b'  # Month abbreviation
        else:
            start_date = today - timedelta(days=30)
            date_format = '%d'
        
        # Borrowings by date
        query = """
            SELECT DATE(borrow_date) as date, COUNT(*) as count
            FROM borrowings
            WHERE borrow_date >= %s
            GROUP BY DATE(borrow_date)
            ORDER BY date
        """
        borrowings_by_date = execute_query(query, [start_date], dictionary=True)
        
        # Format dates
        formatted_borrowings = []
        for item in borrowings_by_date:
            formatted_date = item['date'].strftime(date_format)
            formatted_borrowings.append({
                'date': formatted_date,
                'count': item['count']
            })
        
        stats['borrowings_by_date'] = formatted_borrowings
        
        # Most borrowed books
        query = """
            SELECT b.book_id, b.title, b.author, COUNT(br.borrowing_id) as borrow_count
            FROM books b
            JOIN borrowings br ON b.book_id = br.book_id
            WHERE br.borrow_date >= %s
            GROUP BY b.book_id
            ORDER BY borrow_count DESC
            LIMIT 5
        """
        stats['most_borrowed_books'] = execute_query(query, [start_date], dictionary=True)
        
        # Most active users
        query = """
            SELECT u.user_id, u.username, u.full_name, COUNT(br.borrowing_id) as borrow_count
            FROM users u
            JOIN borrowings br ON u.user_id = br.user_id
            WHERE br.borrow_date >= %s
            GROUP BY u.user_id
            ORDER BY borrow_count DESC
            LIMIT 5
        """
        stats['most_active_users'] = execute_query(query, [start_date], dictionary=True)
        
        return stats