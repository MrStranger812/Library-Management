from utils.db_manager import execute_query, execute_update, insert_and_get_id, get_db_cursor

class EnhancedBook:
    @staticmethod
    def create(isbn, title, author_ids, publisher_id=None, category_id=None, 
               publication_year=None, description=None, total_copies=1):
        """Create a new book with multiple authors"""
        with get_db_cursor() as cursor:
            # Insert book
            book_query = """
                INSERT INTO books (isbn, title, publisher_id, category_id, 
                                 publication_year, description, total_copies, copies_available)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(book_query, (isbn, title, publisher_id, category_id, 
                                      publication_year, description, total_copies, total_copies))
            book_id = cursor.lastrowid
            
            # Insert book-author relationships
            if author_ids:
                author_query = "INSERT INTO book_authors (book_id, author_id, role) VALUES (%s, %s, %s)"
                for author_id in author_ids:
                    cursor.execute(author_query, (book_id, author_id, 'author'))
            
            return book_id
    
    @staticmethod
    def get_with_details(book_id):
        """Get book with full details including authors, publisher, and category"""
        query = """
            SELECT 
                b.book_id, b.isbn, b.title, b.description, b.publication_year,
                b.total_copies, b.copies_available, b.language, b.page_count,
                p.name as publisher_name,
                c.name as category_name,
                GROUP_CONCAT(
                    CONCAT(a.first_name, ' ', a.last_name) 
                    ORDER BY ba.role, a.last_name 
                    SEPARATOR ', '
                ) as authors,
                AVG(br.rating) as average_rating,
                COUNT(br.review_id) as review_count
            FROM books b
            LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
            LEFT JOIN categories c ON b.category_id = c.category_id
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            LEFT JOIN book_reviews br ON b.book_id = br.book_id
            WHERE b.book_id = %s
            GROUP BY b.book_id
        """
        return execute_query(query, (book_id,), dictionary=True, fetchall=False)
    
    @staticmethod
    def search_advanced(filters):
        """Advanced book search with multiple filters"""
        query = """
            SELECT DISTINCT
                b.book_id, b.isbn, b.title, b.publication_year,
                b.copies_available, b.total_copies,
                p.name as publisher_name,
                c.name as category_name,
                GROUP_CONCAT(
                    DISTINCT CONCAT(a.first_name, ' ', a.last_name) 
                    ORDER BY a.last_name 
                    SEPARATOR ', '
                ) as authors
            FROM books b
            LEFT JOIN publishers p ON b.publisher_id = p.publisher_id
            LEFT JOIN categories c ON b.category_id = c.category_id
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            LEFT JOIN book_tag_assignments bta ON b.book_id = bta.book_id
            LEFT JOIN book_tags bt ON bta.tag_id = bt.tag_id
            WHERE 1=1
        """
        params = []
        
        # Add search conditions based on filters
        if filters.get('title'):
            query += " AND b.title LIKE %s"
            params.append(f"%{filters['title']}%")
        
        if filters.get('author'):
            query += " AND CONCAT(a.first_name, ' ', a.last_name) LIKE %s"
            params.append(f"%{filters['author']}%")
        
        if filters.get('isbn'):
            query += " AND b.isbn LIKE %s"
            params.append(f"%{filters['isbn']}%")
        
        if filters.get('category_id'):
            query += " AND b.category_id = %s"
            params.append(filters['category_id'])
        
        if filters.get('publisher_id'):
            query += " AND b.publisher_id = %s"
            params.append(filters['publisher_id'])
        
        if filters.get('year_from'):
            query += " AND b.publication_year >= %s"
            params.append(filters['year_from'])
        
        if filters.get('year_to'):
            query += " AND b.publication_year <= %s"
            params.append(filters['year_to'])
        
        if filters.get('available_only'):
            query += " AND b.copies_available > 0"
        
        if filters.get('tags'):
            tag_placeholders = ','.join(['%s'] * len(filters['tags']))
            query += f" AND bt.tag_id IN ({tag_placeholders})"
            params.extend(filters['tags'])
        
        query += " GROUP BY b.book_id ORDER BY b.title"
        
        return execute_query(query, params, dictionary=True)