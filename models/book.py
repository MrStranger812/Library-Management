# Book model in models/book.py
class Book:
    @staticmethod
    def get_all():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()
        cursor.close()
        return books
    
    @staticmethod
    def get_by_id(book_id):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
        book = cursor.fetchone()
        cursor.close()
        return book
    
    @staticmethod
    def create(isbn, title, author, category, publication_year, copies):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO books (isbn, title, author, category, publication_year, copies_available, total_copies) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (isbn, title, author, category, publication_year, copies, copies)
        )
        mysql.connection.commit()
        book_id = cursor.lastrowid
        cursor.close()
        return book_id
    
    @staticmethod
    def update(book_id, title, author, category, publication_year, copies_available, total_copies):
        cursor = mysql.connection.cursor()
        cursor.execute(
            "UPDATE books SET title = %s, author = %s, category = %s, publication_year = %s, copies_available = %s, total_copies = %s WHERE book_id = %s",
            (title, author, category, publication_year, copies_available, total_copies, book_id)
        )
        mysql.connection.commit()
        cursor.close()
    
    @staticmethod
    def delete(book_id):
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        mysql.connection.commit()
        cursor.close()
    
    @staticmethod
    def search(query):
        cursor = mysql.connection.cursor()
        search_query = f"%{query}%"
        cursor.execute(
            "SELECT * FROM books WHERE title LIKE %s OR author LIKE %s OR isbn LIKE %s OR category LIKE %s",
            (search_query, search_query, search_query, search_query)
        )
        books = cursor.fetchall()
        cursor.close()
        return books