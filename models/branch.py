from utils.db_manager import execute_query

class Branch:
    @staticmethod
    def get_all_branches():
        """Get all library branches"""
        query = """
            SELECT branch_id, name, address, phone, email, 
                   CONCAT(u.first_name, ' ', u.last_name) as manager_name,
                   is_active
            FROM library_branches lb
            LEFT JOIN users u ON lb.manager_id = u.user_id
            WHERE lb.is_active = TRUE
            ORDER BY lb.name
        """
        return execute_query(query, dictionary=True)
    
    @staticmethod
    def get_branch_inventory(branch_id):
        """Get inventory for a specific branch"""
        query = """
            SELECT 
                b.book_id, b.title, b.isbn,
                GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') as authors,
                COUNT(bc.copy_id) as total_copies,
                SUM(CASE WHEN bc.is_available THEN 1 ELSE 0 END) as available_copies
            FROM books b
            JOIN book_copies bc ON b.book_id = bc.book_id
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            WHERE bc.branch_id = %s
            GROUP BY b.book_id
            ORDER BY b.title
        """
        return execute_query(query, (branch_id,), dictionary=True)
