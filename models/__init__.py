"""
Models package for the Library Management System.
This module provides access to all database models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models here to avoid circular imports
# Models will be imported when needed in the application 