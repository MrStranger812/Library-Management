from functools import wraps
from flask import request, current_app
from models.audit_log import AuditLog

def audit_log(action, resource_type=None, resource_id=None, details=None):
    """Decorator for logging actions in the system."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the result of the original function
            result = f(*args, **kwargs)
            
            # Get user information if available
            user_id = None
            if hasattr(request, 'user') and request.user:
                user_id = request.user.user_id
            
            # Create audit log entry
            AuditLog.log_action(
                action=action,
                resource_type=resource_type,
                user_id=user_id,
                resource_id=resource_id,
                details=details,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string
            )
            
            return result
        return decorated_function
    return decorator

def log_action(action, resource_type=None, resource_id=None, details=None):
    """Log an action directly without using the decorator."""
    user_id = None
    if hasattr(request, 'user') and request.user:
        user_id = request.user.user_id
    
    return AuditLog.log_action(
        action=action,
        resource_type=resource_type,
        user_id=user_id,
        resource_id=resource_id,
        details=details,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )

# Common audit actions
class AuditActions:
    # User actions
    USER_LOGIN = 'user_login'
    USER_LOGOUT = 'user_logout'
    USER_CREATE = 'user_create'
    USER_UPDATE = 'user_update'
    USER_DELETE = 'user_delete'
    
    # Book actions
    BOOK_CREATE = 'book_create'
    BOOK_UPDATE = 'book_update'
    BOOK_DELETE = 'book_delete'
    BOOK_BORROW = 'book_borrow'
    BOOK_RETURN = 'book_return'
    BOOK_RESERVE = 'book_reserve'
    
    # Fine actions
    FINE_CREATE = 'fine_create'
    FINE_PAY = 'fine_pay'
    FINE_WAIVE = 'fine_waive'
    
    # Tag actions
    TAG_CREATE = 'tag_create'
    TAG_UPDATE = 'tag_update'
    TAG_DELETE = 'tag_delete'
    TAG_ADD = 'tag_add'
    TAG_REMOVE = 'tag_remove'
    
    # System actions
    SYSTEM_CONFIG_UPDATE = 'system_config_update'
    SYSTEM_BACKUP = 'system_backup'
    SYSTEM_RESTORE = 'system_restore'

# Common resource types
class ResourceTypes:
    USER = 'user'
    BOOK = 'book'
    BORROWING = 'borrowing'
    FINE = 'fine'
    TAG = 'tag'
    SYSTEM = 'system' 