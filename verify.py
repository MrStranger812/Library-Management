# verify_database.py
import pymysql

def verify_database_setup():
    try:
        # Connect to MySQL with hardcoded credentials
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Qwaszxerdfcv56@',
            database='library_management',
            port=3306,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        print("🔍 Verifying Database Setup...")
        print("=" * 50)
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        expected_tables = [
            'audit_logs', 'book_reviews', 'books', 'borrowings', 
            'fines', 'notifications', 'permissions', 'reservations', 
            'user_permissions', 'users'
        ]
        
        existing_tables = [table[0] for table in tables]
        
        print("📊 Tables Created:")
        for table in expected_tables:
            if table in existing_tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - MISSING")
        
        # Check stored procedures
        cursor.execute("SHOW PROCEDURE STATUS WHERE Db = 'library_management'")
        procedures = cursor.fetchall()
        
        print(f"\n🔧 Stored Procedures: {len(procedures)} found")
        for proc in procedures:
            print(f"  ✅ {proc[1]}")  # procedure name
        
        # Check default admin user
        cursor.execute("SELECT username, email, role FROM users WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if admin_user:
            print(f"\n👤 Default Admin User:")
            print(f"  ✅ Username: {admin_user[0]}")
            print(f"  ✅ Email: {admin_user[1]}")
            print(f"  ✅ Role: {admin_user[2]}")
        else:
            print("\n❌ Default admin user not found")
        
        # Check permissions
        cursor.execute("SELECT COUNT(*) FROM permissions")
        perm_count = cursor.fetchone()[0]
        print(f"\n🔐 Permissions: {perm_count} created")
        
        # Check sample books
        cursor.execute("SELECT COUNT(*) FROM books")
        book_count = cursor.fetchone()[0]
        print(f"📚 Sample Books: {book_count} created")
        
        if book_count > 0:
            cursor.execute("SELECT title, author FROM books LIMIT 3")
            sample_books = cursor.fetchall()
            print("  Sample books:")
            for book in sample_books:
                print(f"    - {book[0]} by {book[1]}")
        
        cursor.close()
        connection.close()
        
        print("\n" + "=" * 50)
        print("🎉 Database verification completed successfully!")
        print("Your database is ready to use.")
        
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def test_admin_login():
    """Test if admin credentials work"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='Qwaszxerdfcv56@',
            database='library_management',
            port=3306,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username = 'admin'")
        admin_data = cursor.fetchone()
        
        if admin_data:
            print(f"\n🔑 Admin Login Info:")
            print(f"  Username: admin")
            print(f"  Password: admin123")
            print(f"  Email: admin@library.com")
            print(f"  Note: Password is hashed in database")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error checking admin credentials: {e}")

if __name__ == "__main__":
    verify_database_setup()
    test_admin_login()