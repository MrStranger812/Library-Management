"""
Book models for the Library Management System.
Includes Book, Publisher, Category, Author, BookAuthor, BookCopy, and BookReview models.
"""

from models import db
from datetime import UTC, datetime
from sqlalchemy import CheckConstraint, Index

class Book(db.Model):
    """Model for library books."""
    __tablename__ = 'books'
    
    book_id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.publisher_id', ondelete='SET NULL'), index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'), index=True)
    publication_year = db.Column(db.Integer, index=True)
    description = db.Column(db.Text)
    page_count = db.Column(db.Integer)
    language = db.Column(db.String(50), default='English', index=True)
    cover_image = db.Column(db.String(255))
    added_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), index=True)
    added_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    copies_available = db.Column(db.Integer, nullable=False, default=1, index=True)
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Relationships
    publisher = db.relationship('Publisher', backref=db.backref('books', lazy='dynamic'))
    category = db.relationship('Category', backref=db.backref('books', lazy='dynamic'))
    added_by_user = db.relationship('User', backref=db.backref('added_books', lazy='dynamic'))
    authors = db.relationship('Author', secondary='book_authors', back_populates='books', lazy='dynamic')
    book_authors = db.relationship('BookAuthor', back_populates='book', lazy='dynamic', cascade='all, delete-orphan')
    borrowings = db.relationship('Borrowing', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('BookReview', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    copies = db.relationship('BookCopy', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='book_tag_assignments', backref=db.backref('books', lazy='dynamic'))
    tag_assignments = db.relationship('BookTagAssignment', back_populates='book', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint('total_copies > 0', name='chk_copies_positive'),
        CheckConstraint('copies_available >= 0', name='chk_available_copies'),
        CheckConstraint('copies_available <= total_copies', name='chk_available_not_exceed_total'),
        Index('idx_book_search', 'title', 'author', 'isbn'),
        Index('idx_book_availability', 'copies_available', 'is_active')
    )

    def __init__(self, isbn, title, author, category_id=None, publisher_id=None, 
                 publication_year=None, description=None, total_copies=1, language='English'):
        """Initialize a new book."""
        self.isbn = isbn
        self.title = title
        self.author = author
        self.category_id = category_id
        self.publisher_id = publisher_id
        self.publication_year = publication_year
        self.description = description
        self.total_copies = total_copies
        self.copies_available = total_copies
        self.language = language
        self.is_active = True

    @classmethod
    def get_by_id(cls, book_id):
        """Get a book by its ID."""
        return cls.query.get(book_id)

    @classmethod
    def get_by_isbn(cls, isbn):
        """Get a book by its ISBN."""
        return cls.query.filter_by(isbn=isbn).first()

    @classmethod
    def get_all(cls, active_only=True):
        """Get all books, optionally filtering by active status."""
        query = cls.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.title).all()

    @classmethod
    def search(cls, query, active_only=True):
        """Search books by title, author, or ISBN."""
        search_term = f"%{query}%"
        base_query = cls.query.filter(
            (cls.title.ilike(search_term)) |
            (cls.author.ilike(search_term)) |
            (cls.isbn.ilike(search_term))
        )
        if active_only:
            base_query = base_query.filter_by(is_active=True)
        return base_query.order_by(cls.title).all()

    @classmethod
    def get_available_books(cls):
        """Get all books that have available copies."""
        return cls.query.filter_by(is_active=True).filter(cls.copies_available > 0).all()

    @classmethod
    def get_books_by_category(cls, category_id):
        """Get all books in a specific category."""
        return cls.query.filter_by(category_id=category_id, is_active=True).all()

    @classmethod
    def get_books_by_publisher(cls, publisher_id):
        """Get all books from a specific publisher."""
        return cls.query.filter_by(publisher_id=publisher_id, is_active=True).all()

    @property
    def average_rating(self):
        """Calculate the average rating for the book."""
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    def update_copies(self, new_total):
        """Update the total number of copies and available copies."""
        if new_total < 0:
            raise ValueError("Total copies cannot be negative")
        self.total_copies = new_total
        self.copies_available = max(0, min(self.copies_available, new_total))

    def deactivate(self):
        """Deactivate the book."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self):
        """Activate the book."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def to_dict(self):
        """Convert book object to dictionary."""
        return {
            'book_id': self.book_id,
            'isbn': self.isbn,
            'title': self.title,
            'description': self.description,
            'publication_year': self.publication_year,
            'publisher': self.publisher.name if self.publisher else None,
            'publisher_id': self.publisher_id,
            'category': self.category.name if self.category else None,
            'category_id': self.category_id,
            'language': self.language,
            'page_count': self.page_count,
            'cover_image': self.cover_image,
            'total_copies': self.total_copies,
            'copies_available': self.copies_available,
            'is_active': self.is_active,
            'average_rating': self.average_rating,
            'authors': [{
                'author_id': author.author_id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'role': next((ba.role for ba in self.book_authors if ba.author_id == author.author_id), 'author')
            } for author in self.authors],
            'tags': [tag.name for tag in self.tags],
            'created_at': self.added_at.isoformat() if self.added_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the book."""
        return f'<Book {self.title}>'

class Publisher(db.Model):
    """Model for book publishers."""
    __tablename__ = 'publishers'
    
    publisher_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    address = db.Column(db.Text)
    website = db.Column(db.String(255))
    established_year = db.Column(db.Integer, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = db.Column(db.Boolean, default=True, index=True)

    def __init__(self, name, address=None, website=None, established_year=None):
        """Initialize a new publisher."""
        self.name = name
        self.address = address
        self.website = website
        self.established_year = established_year
        self.is_active = True

    def to_dict(self):
        """Convert publisher to dictionary."""
        return {
            'publisher_id': self.publisher_id,
            'name': self.name,
            'address': self.address,
            'website': self.website,
            'established_year': self.established_year,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the publisher."""
        return f'<Publisher {self.name}>'

class Category(db.Model):
    """Model for book categories."""
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'), index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    is_active = db.Column(db.Boolean, default=True, index=True)

    # Self-referential relationship for parent-child categories
    parent = db.relationship('Category', remote_side=[category_id], backref=db.backref('subcategories', lazy='dynamic'))

    def __init__(self, name, description=None, parent_category_id=None):
        """Initialize a new category."""
        self.name = name
        self.description = description
        self.parent_category_id = parent_category_id
        self.is_active = True

    def to_dict(self):
        """Convert category to dictionary."""
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'parent_category_id': self.parent_category_id,
            'parent_name': self.parent.name if self.parent else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the category."""
        return f'<Category {self.name}>'

class BookCopy(db.Model):
    """Model for individual book copies."""
    __tablename__ = 'book_copies'
    
    copy_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    branch_id = db.Column(db.Integer, db.ForeignKey('library_branches.branch_id', ondelete='CASCADE'), nullable=False, index=True)
    barcode = db.Column(db.String(50), unique=True, index=True)
    acquisition_date = db.Column(db.Date, nullable=False, index=True)
    condition_status = db.Column(db.Enum('excellent', 'good', 'fair', 'poor', 'damaged'), default='good', index=True)
    location = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2))
    is_available = db.Column(db.Boolean, default=True, index=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    def __init__(self, book_id, branch_id, barcode, acquisition_date, condition_status='good',
                 location=None, price=None, notes=None):
        """Initialize a new book copy."""
        self.book_id = book_id
        self.branch_id = branch_id
        self.barcode = barcode
        self.acquisition_date = acquisition_date
        self.condition_status = condition_status
        self.location = location
        self.price = price
        self.notes = notes
        self.is_available = True

    def to_dict(self):
        """Convert book copy to dictionary."""
        return {
            'copy_id': self.copy_id,
            'book_id': self.book_id,
            'branch_id': self.branch_id,
            'barcode': self.barcode,
            'acquisition_date': self.acquisition_date.isoformat() if self.acquisition_date else None,
            'condition_status': self.condition_status,
            'location': self.location,
            'price': float(self.price) if self.price else None,
            'is_available': self.is_available,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        """String representation of the book copy."""
        return f'<BookCopy {self.barcode}>'

class Author(db.Model):
    __tablename__ = 'authors'
    
    author_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    nationality = db.Column(db.String(100), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    books = db.relationship('Book', secondary='book_authors', back_populates='authors')
    book_authors = db.relationship('BookAuthor', back_populates='author', cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_full_name', 'last_name', 'first_name'),
    )

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id', ondelete='CASCADE'), primary_key=True)
    role = db.Column(db.Enum('author', 'co-author', 'editor', 'translator'), default='author')

    # Relationships
    book = db.relationship('Book', back_populates='book_authors')
    author = db.relationship('Author', back_populates='book_authors')

class BookReview(db.Model):
    __tablename__ = 'book_reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False, index=True)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        db.UniqueConstraint('book_id', 'user_id', name='unique_user_book_review')
    )