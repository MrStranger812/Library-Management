from utils.db_manager import execute_query, execute_update, insert_and_get_id

class Author:
    @staticmethod
    def create(first_name, last_name, biography=None, birth_date=None, nationality=None):
        """Create a new author"""
        query = """
            INSERT INTO authors (first_name, last_name, biography, birth_date, nationality)
            VALUES (%s, %s, %s, %s, %s)
        """
        return insert_and_get_id(query, (first_name, last_name, biography, birth_date, nationality))
    
    @staticmethod
    def get_all():
        """Get all authors"""
        query = """
            SELECT author_id, first_name, last_name, biography, birth_date, 
                   death_date, nationality, created_at
            FROM authors
            ORDER BY last_name, first_name
        """
        return execute_query(query, dictionary=True)
    
    @staticmethod
    def get_by_id(author_id):
        """Get author by ID"""
        query = """
            SELECT author_id, first_name, last_name, biography, birth_date, 
                   death_date, nationality, created_at
            FROM authors
            WHERE author_id = %s
        """
        return execute_query(query, (author_id,), dictionary=True, fetchall=False)
    
    @staticmethod
    def search(search_term):
        """Search authors by name"""
        query = """
            SELECT author_id, first_name, last_name, biography, nationality
            FROM authors
            WHERE CONCAT(first_name, ' ', last_name) LIKE %s
               OR first_name LIKE %s
               OR last_name LIKE %s
            ORDER BY last_name, first_name
        """
        pattern = f"%{search_term}%"
        return execute_query(query, (pattern, pattern, pattern), dictionary=True)
