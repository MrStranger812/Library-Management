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

## Security Features

### Authentication & Authorization
- Secure password hashing using Bcrypt
- Session management with Flask-Login
- Role-based access control (Admin, Librarian, Member)
- CSRF protection for all forms
- Secure session configuration with HTTP-only cookies
- Account lockout after multiple failed login attempts

### API Security
- Rate limiting for API endpoints
- API key authentication for external access
- Request validation and sanitization
- Secure headers implementation
- Input validation middleware

### Data Security
- SQL injection prevention using parameterized queries
- XSS protection through template escaping
- Secure file upload handling
- Audit logging for sensitive operations
- Data encryption for sensitive information

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

## Utility Modules

### Core Utilities
- **Security** (`utils/security.py`): Authentication, authorization, and security features
- **Logger** (`utils/logger.py`): Logging functionality with rotation
- **Cache** (`utils/cache.py`): In-memory caching with TTL support
- **Database** (`utils/db_manager.py`): Database connection and query management
- **Configuration** (`utils/config_manager.py`): Environment and config management

### Data Management
- **Export** (`utils/export.py`): Data export to CSV and PDF formats
- **Backup** (`utils/backup.py`): Database backup and restoration
- **File Upload** (`utils/file_upload.py`): Secure file handling
- **Pagination** (`utils/pagination.py`): List pagination utilities

### Business Logic
- **Search** (`utils/search.py`): Advanced search functionality
- **Statistics** (`utils/statistics.py`): Report generation
- **Scheduler** (`utils/scheduler.py`): Background task management
- **Validator** (`utils/validator.py`): Input validation and sanitization

## Models

### User Management
- **User** (`models/user.py`): User authentication and profile management
- **Notification** (`models/notification.py`): User notification system

### Book Management
- **Book** (`models/book.py`): Book catalog and inventory
- **Borrowing** (`models/borrowing.py`): Book borrowing and returns

## Controllers

### Authentication
- **Auth** (`controllers/auth.py`): Login, registration, and password management

### Book Operations
- **Book** (`controllers/book.py`): Book CRUD operations and search

### Administrative
- **Admin** (`controllers/admin.py`): System configuration and user management
- **Report** (`controllers/report.py`): Statistical reports and exports

## Project Structure
```
Library Management System/
├── app.py                  # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── backups/              # Database backup files
├── logs/                 # Application logs
├── models/               # Data models
│   ├── user.py          # User model and authentication
│   ├── book.py          # Book model and operations
│   └── borrowing.py     # Borrowing model and logic
├── controllers/          # Request handlers
│   ├── auth.py          # Authentication controller
│   ├── book.py          # Book management controller
│   └── admin.py         # Admin operations controller
├── static/              # Static assets (CSS, JS, images)
├── templates/           # HTML templates
├── utils/               # Utility modules
│   ├── security.py      # Security utilities
│   ├── logger.py        # Logging utilities
│   └── validator.py     # Input validation
└── tests/               # Test cases
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/library-management.git
cd library-management
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask init-db
```

6. Run the application:
```bash
flask run
```

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions small and focused

### Testing
- Write unit tests for new features
- Maintain test coverage above 80%
- Run tests before committing changes
- Use pytest for testing

### Security Best Practices
- Never commit sensitive data
- Use environment variables for secrets
- Validate all user input
- Keep dependencies updated
- Follow OWASP security guidelines

## Deployment

### Production Setup
1. Configure production settings in `.env`
2. Set up a production WSGI server (Gunicorn/uWSGI)
3. Configure reverse proxy (Nginx/Apache)
4. Set up SSL/TLS certificates
5. Configure database backups

### Monitoring
- Set up application monitoring
- Configure error tracking
- Monitor system resources
- Set up alerting for critical issues

### Backup Strategy
- Daily database backups
- Weekly full system backups
- Off-site backup storage
- Regular backup testing

## API Documentation

### Authentication
All API endpoints require authentication using either:
- Session cookie for web interface
- API key for external access

### Rate Limiting
- 100 requests per hour per IP
- 1000 requests per hour per API key

### Endpoints
[API endpoints documentation...]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Acknowledgments

- Flask framework
- MySQL database
- Bootstrap for UI
- All contributors

