import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    _instance = None
    _loggers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup_logging()
        return cls._instance
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # Create handlers
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        
        # Create default logger
        self._create_logger('app', log_dir, file_formatter, console_handler)
        
        # Create specific loggers
        self._create_logger('db', log_dir, file_formatter, console_handler)
        self._create_logger('auth', log_dir, file_formatter, console_handler)
        self._create_logger('books', log_dir, file_formatter, console_handler)
        self._create_logger('borrowings', log_dir, file_formatter, console_handler)
    
    def _create_logger(self, name, log_dir, file_formatter, console_handler):
        """Create a logger with the given name"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Add file handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, f'{name}.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Add console handler
        logger.addHandler(console_handler)
        
        self._loggers[name] = logger
    
    def get_logger(self, name='app'):
        """Get logger by name"""
        return self._loggers.get(name, self._loggers['app'])

# Create a singleton instance
logger = Logger()

def get_logger(name='app'):
    """Get logger by name"""
    return logger.get_logger(name)