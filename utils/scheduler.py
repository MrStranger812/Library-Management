import threading
import time
import schedule
from datetime import datetime
from utils.logger import get_logger

logger = get_logger('scheduler')

class Scheduler:
    _instance = None
    _running = False
    _thread = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Scheduler, cls).__new__(cls)
            cls._instance._setup_scheduler()
        return cls._instance
    
    def _setup_scheduler(self):
        """Setup scheduler with default jobs"""
        # Clear any existing jobs
        schedule.clear()
        
        # Add default jobs
        from models.notification import Notification
        
        # Check for books due tomorrow every day at 8:00 AM
        schedule.every().day.at("08:00").do(Notification.create_due_date_notifications)
        logger.info("Scheduled daily due date notifications check")
        
        # Check for overdue books every day at 00:01 AM
        schedule.every().day.at("00:01").do(self._update_overdue_books)
        logger.info("Scheduled daily overdue books check")
    
    def _update_overdue_books(self):
        """Update status of overdue books"""
        from utils.db_manager import execute_update
        from models.notification import Notification
        
        try:
            # Update borrowings status to 'overdue' if due_date has passed
            affected_rows = execute_update("""
                UPDATE borrowings 
                SET status = 'overdue' 
                WHERE status = 'borrowed' AND due_date < CURDATE()
            """)
            
            if affected_rows > 0:
                # Get the overdue borrowings to create notifications
                from utils.db_manager import execute_query
                overdue_borrowings = execute_query("""
                    SELECT b.borrowing_id, b.user_id, b.book_id, b.due_date, bk.title
                    FROM borrowings b
                    JOIN books bk ON b.book_id = bk.book_id
                    WHERE b.status = 'overdue' AND b.due_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
                """, dictionary=True)
                
                # Create notifications for newly overdue books
                for borrowing in overdue_borrowings:
                    message = f"Your book '{borrowing['title']}' is now overdue. Please return it as soon as possible to avoid additional fines."
                    Notification.create(
                        borrowing['user_id'],
                        message,
                        'overdue_book',
                        borrowing['borrowing_id']
                    )
            
            logger.info(f"Updated {affected_rows} borrowings to overdue status")
            return True
        except Exception as e:
            logger.error(f"Error updating overdue books: {e}")
            return False
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self._running:
            logger.warning("Scheduler is already running")
            return False
        
        def run_scheduler():
            self._running = True
            logger.info("Scheduler started")
            
            while self._running:
                schedule.run_pending()
                time.sleep(1)
            
            logger.info("Scheduler stopped")
        
        self._thread = threading.Thread(target=run_scheduler)
        self._thread.daemon = True
        self._thread.start()
        return True
    
    def stop(self):
        """Stop the scheduler"""
        if not self._running:
            logger.warning("Scheduler is not running")
            return False
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        
        return True
    
    def add_job(self, job_func, interval='daily', at=None):
        """Add a job to the scheduler"""
        if interval == 'daily' and at:
            schedule.every().day.at(at).do(job_func)
        elif interval == 'hourly':
            schedule.every().hour.do(job_func)
        elif interval == 'weekly' and at:
            schedule.every().week.at(at).do(job_func)
        else:
            logger.error(f"Invalid scheduler interval: {interval}")
            return False
        
        logger.info(f"Added job {job_func.__name__} with interval {interval}")
        return True

# Create a singleton instance
scheduler = Scheduler()