# tests/factories.py
import factory
from factory.alchemy import SQLAlchemyModelFactory
from models import db
from models.user import User
from models.book import Book
from models.publisher import Publisher
from models.category import Category
from models.borrowing import Borrowing
from models.fine import Fine
from datetime import datetime, timedelta

class BaseFactory(SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

class PublisherFactory(BaseFactory):
    class Meta:
        model = Publisher
    
    name = factory.Sequence(lambda n: f"Publisher {n}")
    email = factory.Faker('company_email')
    address = factory.Faker('address')

class CategoryFactory(BaseFactory):
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f"Category {n}")
    description = factory.Faker('text', max_nb_chars=200)

class UserFactory(BaseFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Faker('email')
    full_name = factory.Faker('name')
    role = 'member'
    is_active = True
    
    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        if create:
            obj.set_password(extracted or 'Test123!')

class BookFactory(BaseFactory):
    class Meta:
        model = Book
    
    isbn = factory.Faker('isbn13')
    title = factory.Faker('sentence', nb_words=4)
    author = factory.Faker('name')
    publisher = factory.SubFactory(PublisherFactory)
    category = factory.SubFactory(CategoryFactory)
    publication_year = factory.Faker('year')
    total_copies = 5
    copies_available = 5
    description = factory.Faker('text')

class BorrowingFactory(BaseFactory):
    class Meta:
        model = Borrowing
    
    user = factory.SubFactory(UserFactory)
    book = factory.SubFactory(BookFactory)
    borrow_date = factory.LazyFunction(datetime.now)
    due_date = factory.LazyFunction(lambda: datetime.now() + timedelta(days=14))
    status = 'borrowed'