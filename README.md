# Library Management System

## Project Overview

This Library Management System is a comprehensive web application built with Flask that allows libraries to manage their book inventory, user accounts, borrowing processes, and administrative tasks. The system provides features for book cataloging, user management, borrowing and returning books, generating reports, and performing administrative functions.

## System Architecture

The application follows a Model-View-Controller (MVC) architecture:

- **Models**: Handle data operations and business logic
- **Views**: Render templates and present data to users
- **Controllers**: Process user requests and coordinate between models and views

## Key Features

### Core Features
- User authentication and authorization with role-based access control
- Book catalog management with search and filter capabilities
- Borrowing and returning books with due date tracking
- Fine calculation and management for overdue books
- Book tagging system with color-coded tags
- User preferences and customization
- Audit logging for system activities
- Notification system for users and administrators

### Advanced Features
- Membership types with different borrowing privileges
- Book reviews and ratings
- Library events management
- User reading goals and statistics
- Saved searches and search history
- Book recommendations
- Multiple library branch support
- Author and publisher management

## Security Features

### Authentication & Authorization
- Secure password hashing using Bcrypt
- Session management with Flask-Login
- Role-based access control (Admin, Librarian, Member)
- CSRF protection for all forms
- Secure session configuration with HTTP-only cookies
- Account lockout after multiple failed login attempts

### API Security
- Rate limiting for API endpoints
- API key authentication for external access
- Request validation and sanitization
- Secure headers implementation
- Input validation middleware

### Data Security
- SQL injection prevention using parameterized queries
- XSS protection through template escaping
- Secure file upload handling
- Audit logging for sensitive operations
- Data encryption for sensitive information

## Database Schema

The system uses a comprehensive MySQL database with the following key tables:

### Core Tables
- `users`: User accounts and authentication
- `books`: Book catalog and inventory
- `borrowings`: Book borrowing records
- `fines`: Fine management
- `notifications`: User notifications
- `audit_logs`: System activity tracking

### Enhanced Tables
- `authors`: Author information
- `publishers`: Publisher details
- `categories`: Book categories
- `library_branches`: Multiple library locations
- `book_copies`: Individual book copies
- `membership_types`: Different membership levels
- `user_memberships`: User membership records
- `book_tags`: Book tagging system
- `book_tag_assignments`: Book-tag relationships
- `user_preferences`: User customization settings
- `library_events`: Library event management
- `event_registrations`: Event attendance tracking

### Views and Procedures
- `available_books`: View of currently available books
- `user_borrowing_summary`: User borrowing statistics
- Stored procedures for book borrowing and returning
- Automatic fine calculation and notification
- Overdue book management

## Project Structure
```
Library Management System/
├── app.py                  # Main application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── database/             # Database schema and migrations
├── models/               # Data models
│   ├── user.py          # User model and authentication
│   ├── book.py          # Book model and operations
│   ├── borrowing.py     # Borrowing model and logic
│   ├── fine.py          # Fine management
│   ├── tag.py           # Book tagging system
│   ├── audit_log.py     # Audit logging
│   └── user_preference.py # User preferences
├── templates/           # HTML templates
├── static/             # Static assets (CSS, JS, images)
├── utils/              # Utility modules
│   ├── security.py     # Security utilities
│   ├── logger.py       # Logging utilities
│   ├── validator.py    # Input validation
│   └── statistics.py   # Statistical analysis
└── tests/              # Test cases
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/library-management.git
cd library-management
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
flask init-db
```

6. Run the application:
```bash
flask run
```

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions small and focused

### Testing
- Write unit tests for new features
- Maintain test coverage above 80%
- Run tests before committing changes
- Use pytest for testing

### Security Best Practices
- Never commit sensitive data
- Use environment variables for secrets
- Validate all user input
- Keep dependencies updated
- Follow OWASP security guidelines

## Deployment

### Production Setup
1. Configure production settings in `.env`
2. Set up a production WSGI server (Gunicorn/uWSGI)
3. Configure reverse proxy (Nginx/Apache)
4. Set up SSL/TLS certificates
5. Configure database backups

### Monitoring
- Set up application monitoring
- Configure error tracking
- Monitor system resources
- Set up alerting for critical issues

### Backup Strategy
- Daily database backups
- Weekly full system backups
- Off-site backup storage
- Regular backup testing

## API Documentation

### Authentication
All API endpoints require authentication using either:
- Session cookie for web interface
- API key for external access

### Rate Limiting
- 100 requests per hour per IP
- 1000 requests per hour per API key

### Key Endpoints
- `/api/books`: Book management
- `/api/users`: User management
- `/api/borrowings`: Borrowing operations
- `/api/fines`: Fine management
- `/api/tags`: Book tagging system
- `/api/preferences`: User preferences
- `/api/audit-logs`: Audit log access

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue if needed

## Acknowledgments

- Flask framework
- MySQL database
- Bootstrap for UI
- All contributors

