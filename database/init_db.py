import os
import mysql.connector
from mysql.connector import Error
from pathlib import Path

def init_database():
    try:
        # Read the schema file
        schema_path = Path(__file__).parent / 'schema.sql'
        with open(schema_path, 'r') as file:
            schema_sql = file.read()

        # Connect to MySQL server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''  # Add your MySQL root password here
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Split the schema into individual statements
            statements = schema_sql.split(';')
            
            # Execute each statement
            for statement in statements:
                if statement.strip():
                    try:
                        cursor.execute(statement)
                        connection.commit()
                    except Error as e:
                        print(f"Error executing statement: {e}")
                        print(f"Statement: {statement}")
                        continue

            print("Database initialized successfully!")

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    init_database() 