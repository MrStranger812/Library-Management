-- Database Security Schema for Library Management System
-- This script creates secure database users with minimal required permissions

-- =====================================================
-- 1. CREATE DATABASE USERS AND ROLES
-- =====================================================

-- Drop users if they exist (for clean setup)
DROP USER IF EXISTS 'library_admin'@'%';
DROP USER IF EXISTS 'library_app'@'%';
DROP USER IF EXISTS 'library_readonly'@'%';
DROP USER IF EXISTS 'library_librarian'@'%';
DROP USER IF EXISTS 'library_member'@'%';
DROP USER IF EXISTS 'library_backup'@'%';

-- Create database users with strong passwords
CREATE USER 'library_admin'@'%' IDENTIFIED BY 'Admin_Lib2025!@#';
CREATE USER 'library_app'@'%' IDENTIFIED BY 'App_Connect2025$%^';
CREATE USER 'library_readonly'@'%' IDENTIFIED BY 'ReadOnly_2025&*()';
CREATE USER 'library_librarian'@'%' IDENTIFIED BY 'Librarian_2025#@!';
CREATE USER 'library_member'@'%' IDENTIFIED BY 'Member_2025$&*';
CREATE USER 'library_backup'@'%' IDENTIFIED BY 'Backup_2025!@#$';

-- =====================================================
-- 2. ADMIN USER PERMISSIONS (Database Administrator)
-- =====================================================

-- Full control over library_management database
GRANT ALL PRIVILEGES ON library_management.* TO 'library_admin'@'%';
GRANT CREATE USER ON *.* TO 'library_admin'@'%';
GRANT RELOAD ON *.* TO 'library_admin'@'%';
GRANT PROCESS ON *.* TO 'library_admin'@'%';

-- =====================================================
-- 3. APPLICATION USER PERMISSIONS (Main App Connection)
-- =====================================================

-- Basic database operations
GRANT SELECT, INSERT, UPDATE, DELETE ON library_management.* TO 'library_app'@'%';

-- Stored procedures and functions
GRANT EXECUTE ON library_management.* TO 'library_app'@'%';

-- Table creation and modification (for migrations)
GRANT CREATE, ALTER, DROP, INDEX ON library_management.* TO 'library_app'@'%';

-- Specific table permissions
GRANT SELECT, INSERT, UPDATE ON library_management.users TO 'library_app'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.books TO 'library_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON library_management.borrowings TO 'library_app'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON library_management.reservations TO 'library_app'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.fines TO 'library_app'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.fine_payments TO 'library_app'@'%';

-- =====================================================
-- 4. READ-ONLY USER PERMISSIONS (Reports, Analytics)
-- =====================================================

-- Read-only access to all tables
GRANT SELECT ON library_management.* TO 'library_readonly'@'%';

-- Access to views only
GRANT SELECT ON library_management.available_books TO 'library_readonly'@'%';
GRANT SELECT ON library_management.user_borrowing_summary TO 'library_readonly'@'%';

-- =====================================================
-- 5. LIBRARIAN USER PERMISSIONS (Limited Admin)
-- =====================================================

-- Book management
GRANT SELECT, INSERT, UPDATE ON library_management.books TO 'library_librarian'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.authors TO 'library_librarian'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.publishers TO 'library_librarian'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.categories TO 'library_librarian'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.book_copies TO 'library_librarian'@'%';

-- User management (limited)
GRANT SELECT, UPDATE ON library_management.users TO 'library_librarian'@'%';
GRANT SELECT ON library_management.user_memberships TO 'library_librarian'@'%';

-- Borrowing operations
GRANT SELECT, INSERT, UPDATE ON library_management.borrowings TO 'library_librarian'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON library_management.reservations TO 'library_librarian'@'%';

-- Fine management
GRANT SELECT, INSERT, UPDATE ON library_management.fines TO 'library_librarian'@'%';
GRANT SELECT, INSERT ON library_management.fine_payments TO 'library_librarian'@'%';

-- Events management
GRANT SELECT, INSERT, UPDATE ON library_management.library_events TO 'library_librarian'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.event_registrations TO 'library_librarian'@'%';

-- Notifications
GRANT SELECT, INSERT ON library_management.notifications TO 'library_librarian'@'%';

-- Audit logs (read-only)
GRANT SELECT ON library_management.audit_logs TO 'library_librarian'@'%';

-- =====================================================
-- 6. MEMBER USER PERMISSIONS (Public Interface)
-- =====================================================

-- Limited user operations
GRANT SELECT ON library_management.users TO 'library_member'@'%';
GRANT UPDATE ON library_management.users TO 'library_member'@'%';

-- Book browsing
GRANT SELECT ON library_management.books TO 'library_member'@'%';
GRANT SELECT ON library_management.authors TO 'library_member'@'%';
GRANT SELECT ON library_management.publishers TO 'library_member'@'%';
GRANT SELECT ON library_management.categories TO 'library_member'@'%';
GRANT SELECT ON library_management.available_books TO 'library_member'@'%';

-- Own borrowings and reservations
GRANT SELECT ON library_management.borrowings TO 'library_member'@'%';
GRANT INSERT ON library_management.reservations TO 'library_member'@'%';
GRANT SELECT, UPDATE ON library_management.reservations TO 'library_member'@'%';

-- Own reviews
GRANT SELECT, INSERT, UPDATE ON library_management.book_reviews TO 'library_member'@'%';

-- Own notifications
GRANT SELECT, UPDATE ON library_management.notifications TO 'library_member'@'%';

-- Own fines (read-only)
GRANT SELECT ON library_management.fines TO 'library_member'@'%';

-- Events
GRANT SELECT ON library_management.library_events TO 'library_member'@'%';
GRANT SELECT, INSERT, UPDATE ON library_management.event_registrations TO 'library_member'@'%';

-- =====================================================
-- 7. BACKUP USER PERMISSIONS (Backup Operations)
-- =====================================================

-- Backup and restore permissions
GRANT SELECT, LOCK TABLES ON library_management.* TO 'library_backup'@'%';
GRANT RELOAD ON *.* TO 'library_backup'@'%';
GRANT PROCESS ON *.* TO 'library_backup'@'%';
GRANT SHOW DATABASES ON *.* TO 'library_backup'@'%';

-- =====================================================
-- 8. ROW-LEVEL SECURITY VIEWS
-- =====================================================

DELIMITER //

-- Create a function to get current user ID
CREATE FUNCTION get_current_user_id() 
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN @current_user_id;
END//

-- Users can only see their own borrowings
CREATE OR REPLACE VIEW user_borrowings_secure AS
SELECT b.* FROM borrowings b
WHERE b.user_id = get_current_user_id()//

-- Users can only see their own reservations
CREATE OR REPLACE VIEW user_reservations_secure AS
SELECT r.* FROM reservations r
WHERE r.user_id = get_current_user_id()//

-- Users can only see their own notifications
CREATE OR REPLACE VIEW user_notifications_secure AS
SELECT n.* FROM notifications n
WHERE n.user_id = get_current_user_id()//

-- Users can only see their own fines
CREATE OR REPLACE VIEW user_fines_secure AS
SELECT f.* FROM fines f
JOIN borrowings b ON f.borrowing_id = b.borrowing_id
WHERE b.user_id = get_current_user_id()//

DELIMITER ;

-- =====================================================
-- 9. SECURITY CONSTRAINTS AND TRIGGERS
-- =====================================================

-- Prevent unauthorized user creation
DELIMITER //
CREATE TRIGGER prevent_admin_creation
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'admin' AND @current_user_role != 'admin' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unauthorized: Cannot create admin users';
    END IF;
END//

-- Audit trail for sensitive operations
CREATE TRIGGER audit_user_changes
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, old_values, new_values, created_at)
    VALUES (
        @current_user_id,
        'UPDATE',
        'user',
        NEW.user_id,
        JSON_OBJECT('role', OLD.role, 'is_active', OLD.is_active),
        JSON_OBJECT('role', NEW.role, 'is_active', NEW.is_active),
        NOW()
    );
END//

-- Prevent fine manipulation
CREATE TRIGGER prevent_fine_reduction
BEFORE UPDATE ON fines
FOR EACH ROW
BEGIN
    IF NEW.amount < OLD.amount AND @current_user_role NOT IN ('admin', 'librarian') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Unauthorized: Cannot reduce fine amount';
    END IF;
END//

DELIMITER ;

-- =====================================================
-- 10. PASSWORD POLICIES AND SECURITY SETTINGS
-- =====================================================

-- Set password validation policies
SET GLOBAL validate_password.policy = STRONG;
SET GLOBAL validate_password.length = 12;
SET GLOBAL validate_password.mixed_case_count = 1;
SET GLOBAL validate_password.number_count = 1;
SET GLOBAL validate_password.special_char_count = 1;

-- Connection limits
ALTER USER 'library_app'@'%' WITH MAX_CONNECTIONS_PER_HOUR 1000;
ALTER USER 'library_readonly'@'%' WITH MAX_CONNECTIONS_PER_HOUR 100;
ALTER USER 'library_librarian'@'%' WITH MAX_CONNECTIONS_PER_HOUR 500;
ALTER USER 'library_member'@'%' WITH MAX_CONNECTIONS_PER_HOUR 50;

-- Force password expiration
ALTER USER 'library_admin'@'%' PASSWORD EXPIRE INTERVAL 90 DAY;
ALTER USER 'library_app'@'%' PASSWORD EXPIRE INTERVAL 180 DAY;
ALTER USER 'library_readonly'@'%' PASSWORD EXPIRE INTERVAL 365 DAY;

-- =====================================================
-- 11. REVOKE DANGEROUS PERMISSIONS
-- =====================================================

-- Remove any accidentally granted global privileges
REVOKE ALL PRIVILEGES ON *.* FROM 'library_app'@'%';
REVOKE ALL PRIVILEGES ON *.* FROM 'library_readonly'@'%';
REVOKE ALL PRIVILEGES ON *.* FROM 'library_librarian'@'%';
REVOKE ALL PRIVILEGES ON *.* FROM 'library_member'@'%';

-- Remove DROP permissions from app user
REVOKE DROP ON library_management.* FROM 'library_app'@'%';

-- Remove DELETE permissions for sensitive tables
REVOKE DELETE ON library_management.users FROM 'library_app'@'%';
REVOKE DELETE ON library_management.audit_logs FROM 'library_app'@'%';
REVOKE DELETE ON library_management.fines FROM 'library_app'@'%';

-- =====================================================
-- 12. APPLY ALL CHANGES
-- =====================================================

FLUSH PRIVILEGES;

-- =====================================================
-- 13. VERIFY PERMISSIONS (Optional Check)
-- =====================================================

-- Show grants for verification
-- SHOW GRANTS FOR 'library_app'@'%';
-- SHOW GRANTS FOR 'library_readonly'@'%';
-- SHOW GRANTS FOR 'library_librarian'@'%';
-- SHOW GRANTS FOR 'library_member'@'%';

-- Test connection with limited user
-- mysql -u library_readonly -p -e "SELECT COUNT(*) FROM library_management.books;"

SELECT 'Database security schema applied successfully!' AS status;