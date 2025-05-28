import re
from datetime import datetime

class Validator:
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password(password):
        """
        Validate password strength
        - At least 8 characters
        - Contains at least one digit
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def validate_isbn(isbn):
        """Validate ISBN format (ISBN-10 or ISBN-13)"""
        # Remove hyphens and spaces
        isbn = re.sub(r'[-\s]', '', isbn)
        
        # ISBN-10
        if len(isbn) == 10:
            if not isbn[:-1].isdigit() or not (isbn[-1].isdigit() or isbn[-1].lower() == 'x'):
                return False
            
            # Calculate checksum
            sum = 0
            for i in range(9):
                sum += int(isbn[i]) * (10 - i)
            
            check = 11 - (sum % 11)
            if check == 11:
                check = '0'
            elif check == 10:
                check = 'X'
            else:
                check = str(check)
            
            return isbn[-1].upper() == check.upper()
        
        # ISBN-13
        elif len(isbn) == 13:
            if not isbn.isdigit():
                return False
            
            # Calculate checksum
            sum = 0
            for i in range(12):
                sum += int(isbn[i]) * (1 if i % 2 == 0 else 3)
            
            check = 10 - (sum % 10)
            if check == 10:
                check = 0
            
            return int(isbn[-1]) == check
        
        return False
    
    @staticmethod
    def validate_date(date_str, format='%Y-%m-%d'):
        """Validate date format"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_input(input_str):
        """Sanitize input string to prevent SQL injection and XSS"""
        if input_str is None:
            return None
        
        # Replace potentially dangerous characters
        sanitized = input_str.replace('<', '&lt;').replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;').replace("'", '&#39;')
        
        return sanitized