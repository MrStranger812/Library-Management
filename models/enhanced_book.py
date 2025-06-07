"""
Enhanced Book model for the Library Management System.
Provides advanced book management functionality with detailed information.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.orm import relationship, joinedload
from typing import List, Dict, Optional, Union

class EnhancedBook:
    """Class providing enhanced book management functionality."""
    
    @staticmethod
    def create(isbn: str, title: str, author_ids: List[int], publisher_id: Optional[int] = None,
               category_id: Optional[int] = None, publication_year: Optional[int] = None,
               description: Optional[str] = None, total_copies: int = 1) -> int:
        """
        Create a new book with multiple authors.
        
        Args:
            isbn (str): ISBN of the book
            title (str): Title of the book
            author_ids (List[int]): List of author IDs
            publisher_id (int, optional): ID of the publisher
            category_id (int, optional): ID of the category
            publication_year (int, optional): Year of publication
            description (str, optional): Book description
            total_copies (int): Total number of copies
            
        Returns:
            int: ID of the created book
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        from models.book import Book
        from models.book_author import BookAuthor
        
        if not isbn or not title:
            raise ValueError("ISBN and title are required")
        
        # Create book
        book = Book(
            isbn=isbn,
            title=title,
            publisher_id=publisher_id,
            category_id=category_id,
            publication_year=publication_year,
            description=description,
            total_copies=total_copies,
            copies_available=total_copies
        )
        
        try:
            db.session.add(book)
            db.session.flush()  # Get the book_id without committing
            
            # Create book-author relationships
            if author_ids:
                for author_id in author_ids:
                    book_author = BookAuthor(
                        book_id=book.book_id,
                        author_id=author_id,
                        role='author'
                    )
                    db.session.add(book_author)
            
            db.session.commit()
            return book.book_id
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error creating book: {str(e)}")
    
    @staticmethod
    def get_with_details(book_id: int) -> Optional[Dict]:
        """
        Get book with full details including authors, publisher, and category.
        
        Args:
            book_id (int): ID of the book
            
        Returns:
            Optional[Dict]: Dictionary containing book details or None if not found
        """
        from models.book import Book
        from models.book_review import BookReview
        
        book = Book.query.options(
            joinedload(Book.publisher),
            joinedload(Book.category),
            joinedload(Book.authors),
            joinedload(Book.reviews)
        ).get(book_id)
        
        if not book:
            return None
        
        # Calculate average rating
        avg_rating = db.session.query(
            func.avg(BookReview.rating)
        ).filter_by(book_id=book_id).scalar() or 0
        
        # Get review count
        review_count = db.session.query(
            func.count(BookReview.review_id)
        ).filter_by(book_id=book_id).scalar()
        
        # Format authors string
        authors = ', '.join(
            f"{author.first_name} {author.last_name}"
            for author in book.authors
        )
        
        return {
            'book_id': book.book_id,
            'isbn': book.isbn,
            'title': book.title,
            'description': book.description,
            'publication_year': book.publication_year,
            'total_copies': book.total_copies,
            'copies_available': book.copies_available,
            'language': book.language,
            'page_count': book.page_count,
            'publisher_name': book.publisher.name if book.publisher else None,
            'category_name': book.category.name if book.category else None,
            'authors': authors,
            'average_rating': round(float(avg_rating), 2),
            'review_count': review_count
        }
    
    @staticmethod
    def search_advanced(filters: Dict) -> List[Dict]:
        """
        Advanced book search with multiple filters.
        
        Args:
            filters (Dict): Dictionary containing search filters:
                - title (str): Book title
                - author (str): Author name
                - isbn (str): ISBN
                - category_id (int): Category ID
                - publisher_id (int): Publisher ID
                - year_from (int): Publication year from
                - year_to (int): Publication year to
                - available_only (bool): Only show available books
                - tags (List[int]): List of tag IDs
                
        Returns:
            List[Dict]: List of dictionaries containing book information
        """
        from models.book import Book
        from models.book_tag import BookTag
        
        query = Book.query.options(
            joinedload(Book.publisher),
            joinedload(Book.category),
            joinedload(Book.authors),
            joinedload(Book.tags)
        )
        
        # Apply filters
        if filters.get('title'):
            query = query.filter(Book.title.ilike(f"%{filters['title']}%"))
        
        if filters.get('author'):
            query = query.join(Book.authors).filter(
                or_(
                    func.concat(Book.authors.first_name, ' ', Book.authors.last_name).ilike(f"%{filters['author']}%"),
                    func.concat(Book.authors.last_name, ' ', Book.authors.first_name).ilike(f"%{filters['author']}%")
                )
            )
        
        if filters.get('isbn'):
            query = query.filter(Book.isbn.ilike(f"%{filters['isbn']}%"))
        
        if filters.get('category_id'):
            query = query.filter(Book.category_id == filters['category_id'])
        
        if filters.get('publisher_id'):
            query = query.filter(Book.publisher_id == filters['publisher_id'])
        
        if filters.get('year_from'):
            query = query.filter(Book.publication_year >= filters['year_from'])
        
        if filters.get('year_to'):
            query = query.filter(Book.publication_year <= filters['year_to'])
        
        if filters.get('available_only'):
            query = query.filter(Book.copies_available > 0)
        
        if filters.get('tags'):
            query = query.join(Book.tags).filter(BookTag.tag_id.in_(filters['tags']))
        
        # Execute query and format results
        books = query.order_by(Book.title).all()
        
        return [{
            'book_id': book.book_id,
            'isbn': book.isbn,
            'title': book.title,
            'publication_year': book.publication_year,
            'copies_available': book.copies_available,
            'total_copies': book.total_copies,
            'publisher_name': book.publisher.name if book.publisher else None,
            'category_name': book.category.name if book.category else None,
            'authors': ', '.join(
                f"{author.first_name} {author.last_name}"
                for author in book.authors
            )
        } for book in books]