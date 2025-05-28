# Library Management System

## Project Overview

This Library Management System is a comprehensive web application built with Flask that allows libraries to manage their book inventory, user accounts, borrowing processes, and administrative tasks. The system provides features for book cataloging, user management, borrowing and returning books, generating reports, and performing administrative functions.

## System Architecture

The application follows a Model-View-Controller (MVC) architecture:

- **Models**: Handle data operations and business logic
- **Views**: Render templates and present data to users
- **Controllers**: Process user requests and coordinate between models and views

## Key Features

- User authentication and authorization with role-based access control
- Book catalog management with search and filter capabilities
- Borrowing and returning books with due date tracking
- Fine calculation for overdue books
- Reporting and statistics generation
- Data export to CSV and PDF formats
- Database backup and restoration
- Notification system for users and administrators

## Database Schema

### Database Creation

```sql
-- Create the library management database
CREATE DATABASE IF NOT EXISTS library_management;
USE library_management;
```
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'librarian', 'member') NOT NULL DEFAULT 'member',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    profile_image VARCHAR(255) DEFAULT NULL
);
```
```sql
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publisher VARCHAR(100),
    publication_year INT,
    category VARCHAR(50),
    description TEXT,
    page_count INT,
    language VARCHAR(50) DEFAULT 'English',
    cover_image VARCHAR(255),
    added_by INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    total_copies INT NOT NULL DEFAULT 1,
    copies_available INT NOT NULL DEFAULT 1,
    FOREIGN KEY (added_by) REFERENCES users(user_id) ON DELETE SET NULL
);
```
```sql
CREATE TABLE borrowings (
    borrowing_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    status ENUM('borrowed', 'returned', 'overdue', 'lost') NOT NULL DEFAULT 'borrowed',
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    fine_paid BOOLEAN DEFAULT FALSE,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);
```
```sql
CREATE TABLE reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATE NOT NULL,
    status ENUM('pending', 'fulfilled', 'cancelled', 'expired') NOT NULL DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
);
```
```sql
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    type ENUM('due_date', 'overdue', 'reservation', 'system') NOT NULL DEFAULT 'system',
    related_id INT DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
```
```sql
CREATE TABLE fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    borrowing_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL,
    is_paid BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (borrowing_id) REFERENCES borrowings(borrowing_id) ON DELETE CASCADE
);
```
```sql
CREATE TABLE book_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    user_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY (book_id, user_id)
);
```
```sql
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);
```
```sql
-- Procedure to borrow a book
DELIMITER //
CREATE PROCEDURE borrow_book(
    IN p_user_id INT,
    IN p_book_id INT,
    IN p_borrow_days INT
)
BEGIN
    DECLARE v_copies_available INT;
    DECLARE v_due_date DATE;
    
    -- Check if book is available
    SELECT copies_available INTO v_copies_available FROM books WHERE book_id = p_book_id;
    
    IF v_copies_available > 0 THEN
        -- Calculate due date
        SET v_due_date = DATE_ADD(CURDATE(), INTERVAL p_borrow_days DAY);
        
        -- Create borrowing record
        INSERT INTO borrowings (user_id, book_id, borrow_date, due_date, status)
        VALUES (p_user_id, p_book_id, CURDATE(), v_due_date, 'borrowed');
        
        -- Update book availability
        UPDATE books SET copies_available = copies_available - 1 WHERE book_id = p_book_id;
        
        -- Create notification for due date
        INSERT INTO notifications (user_id, message, type, related_id)
        VALUES (p_user_id, CONCAT('You have borrowed a book. Due date: ', v_due_date), 'due_date', LAST_INSERT_ID());
        
        SELECT 'Book borrowed successfully' AS message;
    ELSE
        SELECT 'Book not available for borrowing' AS message;
    END IF;
END //
DELIMITER ;

-- Procedure to return a book
DELIMITER //
CREATE PROCEDURE return_book(
    IN p_borrowing_id INT
)
BEGIN
    DECLARE v_book_id INT;
    DECLARE v_user_id INT;
    DECLARE v_due_date DATE;
    DECLARE v_days_overdue INT;
    DECLARE v_fine_amount DECIMAL(10, 2);
    DECLARE v_fine_rate DECIMAL(10, 2) DEFAULT 0.50; -- $0.50 per day
    
    -- Get borrowing details
    SELECT book_id, user_id, due_date 
    INTO v_book_id, v_user_id, v_due_date
    FROM borrowings 
    WHERE borrowing_id = p_borrowing_id AND return_date IS NULL;
    
    IF v_book_id IS NOT NULL THEN
        -- Calculate fine if overdue
        IF CURDATE() > v_due_date THEN
            SET v_days_overdue = DATEDIFF(CURDATE(), v_due_date);
            SET v_fine_amount = v_days_overdue * v_fine_rate;
            
            -- Update borrowing with fine
            UPDATE borrowings 
            SET return_date = CURDATE(), 
                status = 'returned',
                fine_amount = v_fine_amount
            WHERE borrowing_id = p_borrowing_id;
            
            -- Create fine record
            IF v_fine_amount > 0 THEN
                INSERT INTO fines (borrowing_id, amount, reason)
                VALUES (p_borrowing_id, v_fine_amount, CONCAT('Overdue by ', v_days_overdue, ' days'));
                
                -- Create notification for fine
                INSERT INTO notifications (user_id, message, type, related_id)
                VALUES (v_user_id, CONCAT('You have a fine of $', v_fine_amount, ' for returning a book ', v_days_overdue, ' days late.'), 'overdue', p_borrowing_id);
            END IF;
        ELSE
            -- Update borrowing without fine
            UPDATE borrowings 
            SET return_date = CURDATE(), 
                status = 'returned'
            WHERE borrowing_id = p_borrowing_id;
        END IF;
        
        -- Update book availability
        UPDATE books SET copies_available = copies_available + 1 WHERE book_id = v_book_id;
        
        SELECT 'Book returned successfully' AS message;
    ELSE
        SELECT 'Invalid borrowing record or book already returned' AS message;
    END IF;
END //
DELIMITER ;

-- Procedure to check for overdue books
DELIMITER //
CREATE PROCEDURE check_overdue_books()
BEGIN
    -- Update status of overdue books
    UPDATE borrowings 
    SET status = 'overdue' 
    WHERE status = 'borrowed' AND due_date < CURDATE();
    
    -- Create notifications for newly overdue books
    INSERT INTO notifications (user_id, message, type, related_id)
    SELECT b.user_id, 
           CONCAT('Your book "', bk.title, '" is now overdue. Please return it as soon as possible.'),
           'overdue',
           b.borrowing_id
    FROM borrowings b
    JOIN books bk ON b.book_id = bk.book_id
    WHERE b.status = 'overdue' AND b.due_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY);
END //
DELIMITER ;
```
```sql
-- Trigger to log book additions
DELIMITER //
CREATE TRIGGER after_book_insert
AFTER INSERT ON books
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details)
    VALUES (NEW.added_by, 'INSERT', 'book', NEW.book_id, CONCAT('Added book: ', NEW.title));
END //
DELIMITER ;

-- Trigger to log book updates
DELIMITER //
CREATE TRIGGER after_book_update
AFTER UPDATE ON books
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details)
    VALUES (NEW.added_by, 'UPDATE', 'book', NEW.book_id, CONCAT('Updated book: ', NEW.title));
END //
DELIMITER ;

-- Trigger to log borrowing status changes
DELIMITER //
CREATE TRIGGER after_borrowing_update
AFTER UPDATE ON borrowings
FOR EACH ROW
BEGIN
    IF OLD.status != NEW.status THEN
        INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details)
        VALUES (NEW.user_id, 'UPDATE', 'borrowing', NEW.borrowing_id, 
                CONCAT('Borrowing status changed from ', OLD.status, ' to ', NEW.status));
    END IF;
END //
DELIMITER ;
```
```
Library Management System/
├── app.py                  # Main application entry point
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── backups/                # Database backup files
├── logs/                   # Application logs
├── models/                 # Data models
├── controllers/            # Request handlers
├── static/                 # Static assets (CSS, JS, images)
├── templates/              # HTML templates
├── utils/                  # Utility modules
└── tests/                  # Test cases
```
Utility Modules
Export Utility (utils/export.py)
Provides functionality to export data in various formats:

export_to_csv(): Exports data to CSV format for download
export_to_pdf(): Exports data to PDF format for download
These functions take data (as lists of dictionaries or tuples), format it appropriately, and return Flask response objects with the correct headers for file downloads.

Database Manager (utils/db_manager.py)
Manages database connections and provides helper functions for database operations:

get_db_cursor(): Context manager for database cursor
execute_query(): Executes SELECT queries and returns results
execute_update(): Executes INSERT/UPDATE/DELETE queries
insert_and_get_id(): Inserts a record and returns the new ID
This module simplifies database operations and ensures proper connection handling.

Configuration Manager (utils/config_manager.py)
Manages application configuration from environment variables and config files:

get(): Retrieves configuration values
set(): Sets configuration values
save_to_file(): Saves configuration to file
Implements the singleton pattern to ensure consistent configuration across the application.

Logger (utils/logger.py)
Provides logging functionality with different log levels and output destinations:

get_logger(): Returns a configured logger for a specific component
Supports file and console logging
Implements log rotation to manage log file sizes
Error Handler (utils/error_handler.py)
Centralizes error handling for the application:

register_error_handlers(): Registers error handlers with Flask
Provides consistent error responses for different error types
Supports both HTML and JSON responses based on request type
Scheduler (utils/scheduler.py)
Manages background tasks and scheduled jobs:

start(): Starts the scheduler in a background thread
stop(): Stops the scheduler
add_job(): Adds a new job to the scheduler
Includes predefined jobs for due date notifications and overdue book status updates
Backup Utility (utils/backup.py)
Provides database backup and restoration functionality:

create_database_backup(): Creates a backup of the database
restore_database_backup(): Restores the database from a backup
list_backups(): Lists available database backups with metadata
This module ensures data safety through regular backups and provides disaster recovery capabilities.

Pagination Utility (utils/pagination.py)
Handles pagination for lists of items:

Pagination class: Manages pagination state and calculations
get_pagination_args(): Extracts pagination parameters from requests
iter_pages(): Generates page numbers for pagination UI
Search Utility (utils/search.py)
Provides advanced search functionality:

search_books(): Searches books with filters and sorting
search_users(): Searches users with filters and sorting
get_book_categories(): Gets all unique book categories
Statistics Utility (utils/statistics.py)
Generates statistics and reports:

get_dashboard_stats(): Gets statistics for the dashboard
get_borrowing_stats(): Gets borrowing statistics for a specific period
Cache Utility (utils/cache.py)
Provides in-memory caching:

get(): Retrieves a value from cache
set(): Stores a value in cache with optional TTL
delete(): Removes a value from cache
clear(): Clears all cache
cached(): Decorator for caching function results
Security Utility (utils/security.py)
Implements security features:

generate_token(): Generates secure random tokens
hash_data(): Hashes data with optional salt
verify_hash(): Verifies data against a hash
rate_limit(): Implements rate limiting
check_ip_rate_limit(): Checks rate limit for current IP address
File Upload Utility (utils/file_upload.py)
Handles file uploads:

save_file(): Saves uploaded files with validation
delete_file(): Deletes files
allowed_file(): Checks if file extension is allowed
Validator (utils/validator.py)
Provides validation functions:

validate_email(): Validates email format
validate_password(): Validates password strength
validate_isbn(): Validates ISBN format
validate_date(): Validates date format
sanitize_input(): Sanitizes input to prevent injection attacks
Models
User Model (models/user.py)
Manages user data and authentication:

User registration, login, and profile management
Password hashing and verification
Role-based permissions
Book Model (models/book.py)
Manages book data:

Book creation, updating, and deletion
Book availability tracking
Book search and filtering
Borrowing Model (models/borrowing.py)
Manages book borrowing:

Borrowing and returning books
Due date tracking
Overdue status and fine calculation
Notification Model (models/notification.py)
Manages user notifications:

Creating notifications
Marking notifications as read
Notification delivery
Controllers
Auth Controller (controllers/auth.py)
Handles authentication and authorization:

Login and logout
User registration
Password reset
Book Controller (controllers/book.py)
Handles book-related operations:

Book listing, creation, editing, and deletion
Book search and filtering
Book import and export
Borrowing Controller (controllers/borrowing.py)
Handles borrowing-related operations:

Borrowing and returning books
Managing overdue books
Calculating fines
Admin Controller (controllers/admin.py)
Handles administrative operations:

User management
System configuration
Database backup and restoration
Report Controller (controllers/report.py)
Handles report generation:

Statistical reports
Usage reports
Exporting reports
Setup and Installation
Clone the repository
Install dependencies: pip install -r requirements.txt
Configure database settings in .env or config.json
Initialize the database: flask init-db
Run the application: flask run
Development
Use virtual environment for development
Follow PEP 8 style guidelines
Write tests for new features
Document code with docstrings
Deployment
Configure production settings
Set up a production WSGI server (Gunicorn, uWSGI)
Use a reverse proxy (Nginx, Apache)
Set up regular database backups
Configure logging for production
License
This project is licensed under the MIT License - see the LICENSE file for details.

