import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigManager:
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from environment variables and config file"""
        # Load from environment variables
        self._config = {
            'MYSQL_HOST': os.getenv('MYSQL_HOST', 'localhost'),
            'MYSQL_USER': os.getenv('MYSQL_USER', 'library_app'),
            'MYSQL_PASSWORD': os.getenv('MYSQL_PASSWORD', ''),
            'MYSQL_DB': os.getenv('MYSQL_DB', 'library_management'),
            'SECRET_KEY': os.getenv('SECRET_KEY', 'default_secret_key'),
            'FINE_RATE_PER_DAY': float(os.getenv('FINE_RATE_PER_DAY', '0.50')),
            'MAX_BORROW_DAYS': int(os.getenv('MAX_BORROW_DAYS', '14')),
            'MAX_BOOKS_PER_USER': int(os.getenv('MAX_BOOKS_PER_USER', '5')),
            'DEBUG': os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
        }
        
        # Try to load from config.json if it exists
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    # Update config with values from file
                    self._config.update(file_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self._config[key] = value
    
    def save_to_file(self):
        """Save current configuration to file"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
        try:
            with open(config_path, 'w') as f:
                json.dump(self._config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config file: {e}")
            return False

# Create a singleton instance
config = ConfigManager()