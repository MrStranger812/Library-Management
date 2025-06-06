# Book model in models/book.py
from extensions import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    
    book_id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.publisher_id', ondelete='SET NULL'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'))
    publication_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    page_count = db.Column(db.Integer)
    language = db.Column(db.String(50), default='English')
    cover_image = db.Column(db.String(255))
    added_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    copies_available = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    publisher = db.relationship('Publisher', backref='books')
    category = db.relationship('Category', backref='books')
    added_by_user = db.relationship('User', backref='added_books')
    authors = db.relationship('Author', secondary='book_authors', back_populates='books')
    book_authors = db.relationship('BookAuthor', back_populates='book', cascade='all, delete-orphan')
    borrowings = db.relationship('Borrowing', backref='book', lazy=True)
    reviews = db.relationship('BookReview', backref='book', lazy=True)
    copies = db.relationship('BookCopy', backref='book', lazy=True)
    tags = db.relationship('BookTag', secondary='book_tag_assignments', backref='books')

    def __init__(self, isbn, title, author, category_id=None, publisher_id=None, 
                 publication_year=None, description=None, total_copies=1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.category_id = category_id
        self.publisher_id = publisher_id
        self.publication_year = publication_year
        self.description = description
        self.total_copies = total_copies
        self.copies_available = total_copies

    @classmethod
    def get_by_id(cls, book_id):
        return cls.query.get(book_id)

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def search(cls, query):
        search_term = f"%{query}%"
        return cls.query.filter(
            (cls.title.ilike(search_term)) |
            (cls.author.ilike(search_term)) |
            (cls.isbn.ilike(search_term))
        ).all()

    def to_dict(self):
        return {
            'book_id': self.book_id,
            'isbn': self.isbn,
            'title': self.title,
            'description': self.description,
            'publication_year': self.publication_year,
            'publisher': self.publisher,
            'language': self.language,
            'page_count': self.page_count,
            'cover_image': self.cover_image,
            'total_copies': self.total_copies,
            'copies_available': self.copies_available,
            'authors': [{
                'author_id': author.author_id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'role': next((ba.role for ba in self.book_authors if ba.author_id == author.author_id), 'author')
            } for author in self.authors],
            'created_at': self.added_at.isoformat() if self.added_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Publisher(db.Model):
    __tablename__ = 'publishers'
    
    publisher_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False)
    address = db.Column(db.Text)
    website = db.Column(db.String(255))
    established_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Self-referential relationship for parent-child categories
    parent = db.relationship('Category', remote_side=[category_id], backref='subcategories')

class Author(db.Model):
    __tablename__ = 'authors'
    
    author_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    biography = db.Column(db.Text)
    birth_date = db.Column(db.Date)
    death_date = db.Column(db.Date)
    nationality = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BookAuthor(db.Model):
    __tablename__ = 'book_authors'
    
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id', ondelete='CASCADE'), primary_key=True)
    role = db.Column(db.Enum('author', 'co-author', 'editor', 'translator'), default='author')

class BookCopy(db.Model):
    __tablename__ = 'book_copies'
    
    copy_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('library_branches.branch_id', ondelete='CASCADE'), nullable=False)
    barcode = db.Column(db.String(50), unique=True)
    acquisition_date = db.Column(db.Date, nullable=False)
    condition_status = db.Column(db.Enum('excellent', 'good', 'fair', 'poor', 'damaged'), default='good')
    location = db.Column(db.String(100))
    price = db.Column(db.Numeric(10, 2))
    is_available = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)

class BookReview(db.Model):
    __tablename__ = 'book_reviews'
    
    review_id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        db.UniqueConstraint('book_id', 'user_id', name='unique_user_book_review')
    )