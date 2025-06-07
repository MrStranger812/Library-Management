"""
UserPreference model for the Library Management System.
Manages user-specific settings and preferences for the library interface.
"""

from datetime import UTC, datetime
from models import db

class UserPreference(db.Model):
    """Model for storing user preferences and settings."""
    __tablename__ = 'user_preferences'
    
    preference_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Notification Preferences
    email_notifications = db.Column(db.Boolean, default=True, index=True)
    sms_notifications = db.Column(db.Boolean, default=False, index=True)
    notification_types = db.Column(db.JSON, default=lambda: {
        'due_date': True,
        'overdue': True,
        'reservation': True,
        'system': True
    })
    
    # Display Preferences
    THEMES = ['light', 'dark', 'system']
    LANGUAGES = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'zh', 'ja', 'ko']
    
    theme = db.Column(db.String(20), default='light', index=True)  # light, dark, system
    language = db.Column(db.String(10), default='en', index=True)  # en, es, fr, etc.
    items_per_page = db.Column(db.Integer, default=10)
    show_cover_images = db.Column(db.Boolean, default=True)
    
    # Search Preferences
    SEARCH_TYPES = ['title', 'author', 'isbn', 'category', 'tag', 'keyword']
    default_search_type = db.Column(db.String(20), default='title', index=True)
    search_history = db.Column(db.JSON, default=list)
    saved_searches = db.Column(db.JSON, default=list)
    
    # Reading Preferences
    preferred_categories = db.Column(db.JSON, default=list)
    preferred_authors = db.Column(db.JSON, default=list)
    reading_goals = db.Column(db.JSON, default=lambda: {
        'books_per_year': 0,
        'pages_per_day': 0
    })
    
    # Privacy Preferences
    show_reading_history = db.Column(db.Boolean, default=True, index=True)
    show_reviews = db.Column(db.Boolean, default=True, index=True)
    allow_recommendations = db.Column(db.Boolean, default=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC))
    
    # Relationships
    user = db.relationship('User', backref=db.backref('preferences', uselist=False, lazy='joined'))
    
    def __init__(self, user_id, **kwargs):
        """Initialize user preferences with default values."""
        self.user_id = user_id
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'theme' and value not in self.THEMES:
                    raise ValueError(f"Invalid theme. Must be one of: {', '.join(self.THEMES)}")
                if key == 'language' and value not in self.LANGUAGES:
                    raise ValueError(f"Invalid language. Must be one of: {', '.join(self.LANGUAGES)}")
                if key == 'default_search_type' and value not in self.SEARCH_TYPES:
                    raise ValueError(f"Invalid search type. Must be one of: {', '.join(self.SEARCH_TYPES)}")
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert preferences to dictionary representation."""
        return {
            'preference_id': self.preference_id,
            'user_id': self.user_id,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'notification_types': self.notification_types,
            'theme': self.theme,
            'language': self.language,
            'items_per_page': self.items_per_page,
            'show_cover_images': self.show_cover_images,
            'default_search_type': self.default_search_type,
            'search_history': self.search_history,
            'saved_searches': self.saved_searches,
            'preferred_categories': self.preferred_categories,
            'preferred_authors': self.preferred_authors,
            'reading_goals': self.reading_goals,
            'show_reading_history': self.show_reading_history,
            'show_reviews': self.show_reviews,
            'allow_recommendations': self.allow_recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'username': self.user.username,
                'full_name': self.user.full_name
            } if self.user else None
        }
    
    def update_preferences(self, **kwargs):
        """Update user preferences with the provided values."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                if key == 'theme' and value not in self.THEMES:
                    raise ValueError(f"Invalid theme. Must be one of: {', '.join(self.THEMES)}")
                if key == 'language' and value not in self.LANGUAGES:
                    raise ValueError(f"Invalid language. Must be one of: {', '.join(self.LANGUAGES)}")
                if key == 'default_search_type' and value not in self.SEARCH_TYPES:
                    raise ValueError(f"Invalid search type. Must be one of: {', '.join(self.SEARCH_TYPES)}")
                setattr(self, key, value)
        self.updated_at = datetime.now(UTC)
    
    def add_search_to_history(self, search_query):
        """Add a search query to the search history."""
        if not isinstance(self.search_history, list):
            self.search_history = []
        
        # Remove duplicate if exists
        if search_query in self.search_history:
            self.search_history.remove(search_query)
        
        # Add to beginning of list
        self.search_history.insert(0, search_query)
        
        # Keep only last 10 searches
        self.search_history = self.search_history[:10]
        self.updated_at = datetime.now(UTC)
    
    def save_search(self, search_name, search_params):
        """Save a search with a name for future use."""
        if not isinstance(self.saved_searches, list):
            self.saved_searches = []
        
        # Check if search with same name exists
        for i, saved_search in enumerate(self.saved_searches):
            if saved_search['name'] == search_name:
                self.saved_searches[i] = {
                    'name': search_name,
                    'params': search_params,
                    'created_at': datetime.now(UTC).isoformat()
                }
                self.updated_at = datetime.now(UTC)
                return
        
        # Add new saved search
        self.saved_searches.append({
            'name': search_name,
            'params': search_params,
            'created_at': datetime.now(UTC).isoformat()
        })
        self.updated_at = datetime.now(UTC)
    
    def remove_saved_search(self, search_name):
        """Remove a saved search by name."""
        if not isinstance(self.saved_searches, list):
            return
        
        self.saved_searches = [
            search for search in self.saved_searches
            if search['name'] != search_name
        ]
        self.updated_at = datetime.now(UTC)
    
    def update_reading_goals(self, books_per_year=None, pages_per_day=None):
        """Update reading goals."""
        if not isinstance(self.reading_goals, dict):
            self.reading_goals = {}
        
        if books_per_year is not None:
            self.reading_goals['books_per_year'] = max(0, books_per_year)
        if pages_per_day is not None:
            self.reading_goals['pages_per_day'] = max(0, pages_per_day)
        self.updated_at = datetime.now(UTC)
    
    def add_preferred_category(self, category):
        """Add a category to preferred categories."""
        if not isinstance(self.preferred_categories, list):
            self.preferred_categories = []
        
        if category not in self.preferred_categories:
            self.preferred_categories.append(category)
            self.updated_at = datetime.now(UTC)
    
    def remove_preferred_category(self, category):
        """Remove a category from preferred categories."""
        if not isinstance(self.preferred_categories, list):
            return
        
        if category in self.preferred_categories:
            self.preferred_categories.remove(category)
            self.updated_at = datetime.now(UTC)
    
    def add_preferred_author(self, author_id):
        """Add an author to preferred authors."""
        if not isinstance(self.preferred_authors, list):
            self.preferred_authors = []
        
        if author_id not in self.preferred_authors:
            self.preferred_authors.append(author_id)
            self.updated_at = datetime.now(UTC)
    
    def remove_preferred_author(self, author_id):
        """Remove an author from preferred authors."""
        if not isinstance(self.preferred_authors, list):
            return
        
        if author_id in self.preferred_authors:
            self.preferred_authors.remove(author_id)
            self.updated_at = datetime.now(UTC)
    
    @classmethod
    def get_by_user_id(cls, user_id):
        """Get user preferences by user ID."""
        return cls.query.filter_by(user_id=user_id).first()
    
    @classmethod
    def create_default(cls, user_id):
        """Create default preferences for a new user."""
        return cls(user_id=user_id)
    
    @classmethod
    def get_users_by_notification_preference(cls, notification_type, enabled=True):
        """Get users with specific notification preference."""
        return cls.query.filter(
            cls.notification_types[notification_type].astext.cast(db.Boolean) == enabled
        ).all()
    
    @classmethod
    def get_users_by_theme(cls, theme):
        """Get users with specific theme preference."""
        return cls.query.filter_by(theme=theme).all()
    
    @classmethod
    def get_users_by_language(cls, language):
        """Get users with specific language preference."""
        return cls.query.filter_by(language=language).all()
    
    def __repr__(self):
        """String representation of the user preferences."""
        return f'<UserPreference {self.preference_id}: User {self.user_id}>' 