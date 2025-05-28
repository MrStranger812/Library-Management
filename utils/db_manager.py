from flask_mysqldb import MySQL
from app import mysql
from contextlib import contextmanager

@contextmanager
def get_db_cursor(dictionary=False):
    """
    Context manager for database cursor
    
    Args:
        dictionary: If True, returns rows as dictionaries
    
    Yields:
        MySQL cursor
    """
    cursor = mysql.connection.cursor(dictionary=dictionary) if dictionary else mysql.connection.cursor()
    try:
        yield cursor
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def execute_query(query, params=None, dictionary=False, fetchall=True):
    """
    Execute a database query
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dictionary)
        dictionary: If True, returns rows as dictionaries
        fetchall: If True, fetches all rows, otherwise fetches one
    
    Returns:
        Query results
    """
    with get_db_cursor(dictionary) as cursor:
        cursor.execute(query, params or ())
        if fetchall:
            return cursor.fetchall()
        return cursor.fetchone()

def execute_update(query, params=None):
    """
    Execute an update/insert/delete query
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dictionary)
    
    Returns:
        Number of affected rows
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.rowcount

def insert_and_get_id(query, params=None):
    """
    Execute an insert query and return the last inserted ID
    
    Args:
        query: SQL query string
        params: Query parameters (tuple or dictionary)
    
    Returns:
        Last inserted ID
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.lastrowid