from utils.db_manager import execute_query  # Adjust the import path as needed

class EnhancedStatistics:
    @staticmethod
    def get_branch_statistics(branch_id=None):
        """Get statistics for a specific branch or all branches"""
        base_query = """
            SELECT 
                br.branch_id,
                br.name as branch_name,
                COUNT(DISTINCT bc.copy_id) as total_books,
                COUNT(DISTINCT CASE WHEN bc.is_available THEN bc.copy_id END) as available_books,
                COUNT(DISTINCT b.borrowing_id) as active_borrowings,
                COUNT(DISTINCT CASE WHEN b.status = 'overdue' THEN b.borrowing_id END) as overdue_borrowings
            FROM library_branches br
            LEFT JOIN book_copies bc ON br.branch_id = bc.branch_id
            LEFT JOIN borrowings b ON bc.copy_id = b.copy_id AND b.status IN ('borrowed', 'overdue')
            WHERE br.is_active = TRUE
        """
        
        if branch_id:
            base_query += " AND br.branch_id = %s"
            params = (branch_id,)
        else:
            params = ()
        
        base_query += " GROUP BY br.branch_id ORDER BY br.name"
        
        return execute_query(base_query, params, dictionary=True)
    
    @staticmethod
    def get_membership_statistics():
        """Get membership type statistics"""
        query = """
            SELECT 
                mt.name as membership_type,
                COUNT(um.membership_id) as total_members,
                COUNT(CASE WHEN um.end_date > CURDATE() THEN 1 END) as active_members,
                AVG(DATEDIFF(um.end_date, um.start_date)) as avg_duration_days
            FROM membership_types mt
            LEFT JOIN user_memberships um ON mt.membership_type_id = um.membership_type_id
            GROUP BY mt.membership_type_id
            ORDER BY active_members DESC
        """
        return execute_query(query, dictionary=True)