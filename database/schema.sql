-- Library Management System Database Schema
-- Combined schema from basic.sql and enhanced.sql

-- Create the database
CREATE DATABASE IF NOT EXISTS library_management;
USE library_management;

-- Create authors table (from enhanced.sql)
CREATE TABLE authors (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    biography TEXT,
    birth_date DATE,
    death_date DATE,
    nationality VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_full_name (last_name, first_name),
    INDEX idx_nationality (nationality)
);

-- Create publishers table (from enhanced.sql)
CREATE TABLE publishers (
    publisher_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    address TEXT,
    website VARCHAR(255),
    established_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_name (name)
);

-- Create categories table (from enhanced.sql)
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_category_id INT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_parent (parent_category_id)
);

-- Create users table (from basic.sql)
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
    profile_image VARCHAR(255) DEFAULT NULL,
    
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active),
    CONSTRAINT chk_email_format CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create library_branches table (from enhanced.sql)
CREATE TABLE library_branches (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    address TEXT NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    manager_id INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (manager_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_name (name),
    INDEX idx_is_active (is_active)
);

-- Create books table (modified from basic.sql)
CREATE TABLE books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    isbn VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(100) NOT NULL,
    publisher_id INT,
    category_id INT,
    publication_year INT,
    description TEXT,
    page_count INT,
    language VARCHAR(50) DEFAULT 'English',
    cover_image VARCHAR(255),
    added_by INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    total_copies INT NOT NULL DEFAULT 1,
    copies_available INT NOT NULL DEFAULT 1,
    
    FOREIGN KEY (publisher_id) REFERENCES publishers(publisher_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (added_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_isbn (isbn),
    INDEX idx_title (title),
    INDEX idx_author (author),
    INDEX idx_copies_available (copies_available),
    CONSTRAINT chk_copies_positive CHECK (total_copies > 0),
    CONSTRAINT chk_available_copies CHECK (copies_available >= 0),
    CONSTRAINT chk_available_not_exceed_total CHECK (copies_available <= total_copies)
);

-- Create book_authors junction table (from enhanced.sql)
CREATE TABLE book_authors (
    book_id INT,
    author_id INT,
    role ENUM('author', 'co-author', 'editor', 'translator') DEFAULT 'author',
    
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);

-- Create book_copies table (from enhanced.sql)
CREATE TABLE book_copies (
    copy_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    branch_id INT NOT NULL,
    barcode VARCHAR(50) UNIQUE,
    acquisition_date DATE NOT NULL,
    condition_status ENUM('excellent', 'good', 'fair', 'poor', 'damaged') DEFAULT 'good',
    location VARCHAR(100),
    price DECIMAL(10, 2),
    is_available BOOLEAN DEFAULT TRUE,
    notes TEXT,
    
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (branch_id) REFERENCES library_branches(branch_id) ON DELETE CASCADE,
    INDEX idx_book_id (book_id),
    INDEX idx_branch_id (branch_id),
    INDEX idx_barcode (barcode),
    INDEX idx_is_available (is_available)
);

-- Create membership_types table (from enhanced.sql)
CREATE TABLE membership_types (
    membership_type_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    max_books_allowed INT DEFAULT 5,
    loan_duration_days INT DEFAULT 14,
    fine_rate_per_day DECIMAL(5, 2) DEFAULT 0.50,
    annual_fee DECIMAL(10, 2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    
    INDEX idx_name (name),
    INDEX idx_is_active (is_active)
);

-- Create user_memberships table (from enhanced.sql)
CREATE TABLE user_memberships (
    membership_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    membership_type_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (membership_type_id) REFERENCES membership_types(membership_type_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_membership_type (membership_type_id),
    INDEX idx_dates (start_date, end_date),
    INDEX idx_is_active (is_active)
);

-- Create borrowings table (modified from basic.sql)
CREATE TABLE borrowings (
    borrowing_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    copy_id INT,
    borrow_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE DEFAULT NULL,
    status ENUM('borrowed', 'returned', 'overdue', 'lost') NOT NULL DEFAULT 'borrowed',
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    fine_paid BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (copy_id) REFERENCES book_copies(copy_id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_status (status),
    INDEX idx_due_date (due_date),
    INDEX idx_borrow_date (borrow_date)
);

-- Create reservations table (from basic.sql)
CREATE TABLE reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATE NOT NULL,
    status ENUM('pending', 'fulfilled', 'cancelled', 'expired') NOT NULL DEFAULT 'pending',
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_status (status),
    INDEX idx_expiry_date (expiry_date)
);

-- Create notifications table (from basic.sql)
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    type ENUM('due_date', 'overdue', 'reservation', 'system') NOT NULL DEFAULT 'system',
    related_id INT DEFAULT NULL,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_is_read (is_read),
    INDEX idx_type (type),
    INDEX idx_created_at (created_at)
);

-- Create fines table (from basic.sql)
CREATE TABLE fines (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    borrowing_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL,
    is_paid BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (borrowing_id) REFERENCES borrowings(borrowing_id) ON DELETE CASCADE,
    INDEX idx_borrowing_id (borrowing_id),
    INDEX idx_is_paid (is_paid),
    INDEX idx_created_at (created_at)
);

-- Create fine_payments table (from enhanced.sql)
CREATE TABLE fine_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    fine_id INT NOT NULL,
    amount_paid DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('cash', 'card', 'online', 'cheque') NOT NULL,
    payment_reference VARCHAR(100),
    paid_by INT,
    paid_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    
    FOREIGN KEY (fine_id) REFERENCES fines(fine_id) ON DELETE CASCADE,
    FOREIGN KEY (paid_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_fine_id (fine_id),
    INDEX idx_payment_method (payment_method),
    INDEX idx_paid_at (paid_at)
);

-- Create book_reviews table (from basic.sql)
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
    UNIQUE KEY unique_user_book_review (book_id, user_id),
    INDEX idx_book_id (book_id),
    INDEX idx_user_id (user_id),
    INDEX idx_rating (rating)
);

-- Create audit_logs table (from basic.sql)
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_entity_type (entity_type),
    INDEX idx_timestamp (timestamp)
);

-- Create permissions table (from basic.sql)
CREATE TABLE permissions (
    permission_id INT AUTO_INCREMENT PRIMARY KEY,
    permission_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_permissions table (from basic.sql)
CREATE TABLE user_permissions (
    user_permission_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    granted_by INT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_permission (user_id, permission_id),
    INDEX idx_user_id (user_id),
    INDEX idx_permission_id (permission_id)
);

-- Create library_events table (from enhanced.sql)
CREATE TABLE library_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    branch_id INT,
    organizer_id INT,
    max_participants INT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (branch_id) REFERENCES library_branches(branch_id) ON DELETE SET NULL,
    FOREIGN KEY (organizer_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_event_date (event_date),
    INDEX idx_branch_id (branch_id),
    INDEX idx_is_active (is_active)
);

-- Create event_registrations table (from enhanced.sql)
CREATE TABLE event_registrations (
    registration_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('registered', 'attended', 'cancelled', 'no_show') DEFAULT 'registered',
    
    FOREIGN KEY (event_id) REFERENCES library_events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_event_user (event_id, user_id),
    INDEX idx_event_id (event_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- Create user_preferences table (from enhanced.sql)
CREATE TABLE user_preferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    preference_name VARCHAR(100) NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_preference (user_id, preference_name),
    INDEX idx_user_id (user_id),
    INDEX idx_preference_name (preference_name)
);

-- Create book_tags table
CREATE TABLE book_tags (
    tag_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7) DEFAULT '#6c757d',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_name (name)
);

-- Create book_tag_assignments table
CREATE TABLE book_tag_assignments (
    book_id INT,
    tag_id INT,
    added_by INT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (book_id, tag_id),
    FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES book_tags(tag_id) ON DELETE CASCADE,
    FOREIGN KEY (added_by) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Insert default data
INSERT INTO permissions (permission_name, description) VALUES
('manage_books', 'Add, edit, and delete books'),
('manage_users', 'Add, edit, and delete users'),
('manage_permissions', 'Grant and revoke permissions'),
('borrow_books', 'Borrow books from the library'),
('return_books', 'Return borrowed books'),
('view_reports', 'View library reports'),
('manage_system', 'System administration and configuration');

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password, email, full_name, role) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3hPyY6s2AW', 'admin@library.com', 'System Administrator', 'admin');

-- Grant all permissions to admin
INSERT INTO user_permissions (user_id, permission_id, granted_by)
SELECT 
    (SELECT user_id FROM users WHERE username = 'admin'),
    permission_id,
    (SELECT user_id FROM users WHERE username = 'admin')
FROM permissions;

-- Insert default membership types
INSERT INTO membership_types (name, description, max_books_allowed, loan_duration_days, fine_rate_per_day, annual_fee) VALUES
('Student', 'Student membership with extended loan period', 10, 21, 0.25, 0.00),
('Regular', 'Standard adult membership', 5, 14, 0.50, 25.00),
('Premium', 'Premium membership with extended privileges', 15, 30, 0.30, 75.00),
('Senior', 'Senior citizen membership with reduced fees', 8, 21, 0.25, 10.00);

-- Insert default categories
INSERT INTO categories (name, description) VALUES
('Fiction', 'Fictional literature and novels'),
('Non-Fiction', 'Factual and educational books'),
('Science', 'Scientific and technical books'),
('History', 'Historical books and biographies'),
('Arts', 'Books about arts, music, and culture'),
('Children', 'Books for children and young adults'),
('Reference', 'Reference materials and encyclopedias'),
('Programming', 'Computer programming and software development');

-- Insert default library branches
INSERT INTO library_branches (name, address, phone, email) VALUES
('Main Branch', '123 Library Street, City Center', '555-0001', 'main@library.com'),
('North Branch', '456 North Avenue, North District', '555-0002', 'north@library.com'),
('South Branch', '789 South Road, South District', '555-0003', 'south@library.com');

-- Create views
CREATE OR REPLACE VIEW available_books AS
SELECT 
    b.book_id,
    b.isbn,
    b.title,
    GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') as authors,
    p.name as publisher,
    c.name as category,
    b.publication_year,
    b.copies_available,
    b.total_copies
FROM books b
LEFT JOIN book_authors ba ON b.book_id = ba.book_id
LEFT JOIN authors a ON ba.author_id = a.author_id
LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
LEFT JOIN categories c ON b.category_id = c.category_id
WHERE b.copies_available > 0
GROUP BY b.book_id;

CREATE OR REPLACE VIEW user_borrowing_summary AS
SELECT 
    u.user_id,
    u.username,
    u.full_name,
    COUNT(CASE WHEN b.status = 'borrowed' THEN 1 END) as current_books,
    COUNT(CASE WHEN b.status = 'overdue' THEN 1 END) as overdue_books,
    SUM(CASE WHEN f.is_paid = FALSE THEN f.amount ELSE 0 END) as unpaid_fines,
    COUNT(b.borrowing_id) as total_borrowings
FROM users u
LEFT JOIN borrowings b ON u.user_id = b.user_id
LEFT JOIN fines f ON b.borrowing_id = f.borrowing_id
GROUP BY u.user_id;

-- Create stored procedures
DELIMITER //

CREATE PROCEDURE borrow_book(
    IN p_user_id INT,
    IN p_book_id INT,
    IN p_borrow_days INT
)
BEGIN
    DECLARE v_copies_available INT;
    DECLARE v_due_date DATE;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
    -- Check if book is available
    SELECT copies_available INTO v_copies_available 
    FROM books WHERE book_id = p_book_id FOR UPDATE;
    
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
        
        COMMIT;
        SELECT 'Book borrowed successfully' AS message;
    ELSE
        ROLLBACK;
        SELECT 'Book not available for borrowing' AS message;
    END IF;
END //

CREATE PROCEDURE return_book(
    IN p_borrowing_id INT
)
BEGIN
    DECLARE v_book_id INT;
    DECLARE v_user_id INT;
    DECLARE v_due_date DATE;
    DECLARE v_days_overdue INT;
    DECLARE v_fine_amount DECIMAL(10, 2);
    DECLARE v_fine_rate DECIMAL(10, 2) DEFAULT 0.50;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;
    
    START TRANSACTION;
    
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
        
        COMMIT;
        SELECT 'Book returned successfully' AS message;
    ELSE
        ROLLBACK;
        SELECT 'Invalid borrowing record or book already returned' AS message;
    END IF;
END //

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

CREATE PROCEDURE GetUserBorrowingLimit(
    IN p_user_id INT,
    OUT p_max_books INT,
    OUT p_current_books INT,
    OUT p_can_borrow BOOLEAN
)
BEGIN
    DECLARE v_membership_type_id INT;
    
    -- Get user's current membership type
    SELECT mt.membership_type_id, mt.max_books_allowed 
    INTO v_membership_type_id, p_max_books
    FROM user_memberships um
    JOIN membership_types mt ON um.membership_type_id = mt.membership_type_id
    WHERE um.user_id = p_user_id AND um.is_active = TRUE
    ORDER BY um.end_date DESC
    LIMIT 1;
    
    -- If no membership found, use default
    IF p_max_books IS NULL THEN
        SET p_max_books = 5;
    END IF;
    
    -- Get current borrowed books count
    SELECT COUNT(*) INTO p_current_books
    FROM borrowings
    WHERE user_id = p_user_id AND status IN ('borrowed', 'overdue');
    
    -- Check if user can borrow more books
    SET p_can_borrow = (p_current_books < p_max_books);
END //

DELIMITER ;

-- Create triggers
DELIMITER //

CREATE TRIGGER after_book_insert
AFTER INSERT ON books
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details)
    VALUES (NEW.added_by, 'INSERT', 'book', NEW.book_id, CONCAT('Added book: ', NEW.title));
END //

CREATE TRIGGER after_book_update
AFTER UPDATE ON books
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details)
    VALUES (NEW.added_by, 'UPDATE', 'book', NEW.book_id, CONCAT('Updated book: ', NEW.title));
END //

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

SELECT 'Database schema created successfully!' AS message; 