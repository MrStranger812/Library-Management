from utils.db_manager import execute_query
from utils.pagination import Pagination, get_pagination_args

class Search:
    @staticmethod
    def search_books(search_term=None, filters=None, sort_by='title', sort_order='asc'):
        """
        Search books with filters and sorting
        
        Args:
            search_term: Search term for title, author, or ISBN
            filters: Dictionary of filters (category, year, etc.)
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
        
        Returns:
            List of books matching the criteria
        """
        # Base query
        query = """
            SELECT b.book_id, b.isbn, b.title, b.author, b.category, 
                   b.publication_year, b.copies_available, b.total_copies
            FROM books b
            WHERE 1=1
        """
        params = []
        
        # Add search term
        if search_term:
            query += """ 
                AND (
                    b.title LIKE %s OR 
                    b.author LIKE %s OR 
                    b.isbn LIKE %s
                )
            """
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # Add filters
        if filters:
            if 'category' in filters and filters['category']:
                query += " AND b.category = %s"
                params.append(filters['category'])
            
            if 'year_from' in filters and filters['year_from']:
                query += " AND b.publication_year >= %s"
                params.append(filters['year_from'])
            
            if 'year_to' in filters and filters['year_to']:
                query += " AND b.publication_year <= %s"
                params.append(filters['year_to'])
            
            if 'availability' in filters:
                if filters['availability'] == 'available':
                    query += " AND b.copies_available > 0"
                elif filters['availability'] == 'unavailable':
                    query += " AND b.copies_available = 0"
        
        # Add sorting
        valid_sort_fields = ['title', 'author', 'category', 'publication_year', 'copies_available']
        if sort_by not in valid_sort_fields:
            sort_by = 'title'
        
        sort_order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        query += f" ORDER BY b.{sort_by} {sort_order}"
        
        # Get pagination parameters
        page, per_page = get_pagination_args()
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count
            FROM books b
            WHERE 1=1
        """
        
        # Add search term to count query
        if search_term:
            count_query += """ 
                AND (
                    b.title LIKE %s OR 
                    b.author LIKE %s OR 
                    b.isbn LIKE %s
                )
            """
        
        # Add filters to count query
        if filters:
            if 'category' in filters and filters['category']:
                count_query += " AND b.category = %s"
            
            if 'year_from' in filters and filters['year_from']:
                count_query += " AND b.publication_year >= %s"
            
            if 'year_to' in filters and filters['year_to']:
                count_query += " AND b.publication_year <= %s"
            
            if 'availability' in filters:
                if filters['availability'] == 'available':
                    count_query += " AND b.copies_available > 0"
                elif filters['availability'] == 'unavailable':
                    count_query += " AND b.copies_available = 0"
        
        # Execute count query
        count_result = execute_query(count_query, params, dictionary=True, fetchall=False)
        total_count = count_result['count'] if count_result else 0
        
        # Add pagination to main query
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        
        # Execute main query
        books = execute_query(query, params, dictionary=True)
        
        # Create pagination object
        pagination = Pagination(page, per_page, total_count)
        
        return books, pagination
    
    @staticmethod
    def get_book_categories():
        """Get all unique book categories"""
        query = "SELECT DISTINCT category FROM books ORDER BY category"
        categories = execute_query(query, dictionary=True)
        return [category['category'] for category in categories]
    
    @staticmethod
    def search_users(search_term=None, role=None, sort_by='username', sort_order='asc'):
        """
        Search users
        
        Args:
            search_term: Search term for username, full_name, or email
            role: Filter by role
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
        
        Returns:
            List of users matching the criteria
        """
        # Base query
        query = """
            SELECT u.user_id, u.username, u.full_name, u.email, u.role, u.created_at
            FROM users u
            WHERE 1=1
        """
        params = []
        
        # Add search term
        if search_term:
            query += """ 
                AND (
                    u.username LIKE %s OR 
                    u.full_name LIKE %s OR 
                    u.email LIKE %s
                )
            """
            search_pattern = f"%{search_term}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        # Add role filter
        if role:
            query += " AND u.role = %s"
            params.append(role)
        
        # Add sorting
        valid_sort_fields = ['username', 'full_name', 'email', 'role', 'created_at']
        if sort_by not in valid_sort_fields:
            sort_by = 'username'
        
        sort_order = 'DESC' if sort_order.lower() == 'desc' else 'ASC'
        query += f" ORDER BY u.{sort_by} {sort_order}"
        
        # Get pagination parameters
        page, per_page = get_pagination_args()
        
        # Get total count
        count_query = f"""
            SELECT COUNT(*) as count
            FROM users u
            WHERE 1=1
        """
        
        # Add search term to count query
        if search_term:
            count_query += """ 
                AND (
                    u.username LIKE %s OR 
                    u.full_name LIKE %s OR 
                    u.email LIKE %s
                )
            """
        
        # Add role filter to count query
        if role:
            count_query += " AND u.role = %s"
        
        # Execute count query
        count_result = execute_query(count_query, params, dictionary=True, fetchall=False)
        total_count = count_result['count'] if count_result else 0
        
        # Add pagination to main query
        query += " LIMIT %s OFFSET %s"
        params.extend([per_page, (page - 1) * per_page])
        
        # Execute main query
        users = execute_query(query, params, dictionary=True)
        
        # Create pagination object
        pagination = Pagination(page, per_page, total_count)
        
        return users, pagination