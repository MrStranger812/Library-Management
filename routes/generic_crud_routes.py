"""
Generic CRUD routes to eliminate DRY violations in route patterns
"""

from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from utils.security import permission_required
from utils.pagination import get_pagination_args, Pagination
from utils.api_response import ApiResponse
from utils.validation import validate_json_schema_decorator
from functools import wraps

class CRUDBlueprint:
    """Generic CRUD operations for models"""
    
    def __init__(self, name, model_class, permission_prefix=None, validation_schemas=None):
        self.name = name
        self.model_class = model_class
        self.permission_prefix = permission_prefix or name
        self.validation_schemas = validation_schemas or {}
        self.blueprint = Blueprint(f'{name}_api', __name__)
        self._register_routes()
    
    def _register_routes(self):
        """Register CRUD routes"""
        # GET /<resource> - List all
        self.blueprint.add_url_rule(
            f'/api/{self.name}',
            f'get_{self.name}',
            self.get_all,
            methods=['GET']
        )
        
        # GET /<resource>/<id> - Get one
        self.blueprint.add_url_rule(
            f'/api/{self.name}/<int:id>',
            f'get_{self.name}_by_id',
            self.get_by_id,
            methods=['GET']
        )
        
        # POST /<resource> - Create
        self.blueprint.add_url_rule(
            f'/api/{self.name}',
            f'create_{self.name}',
            self.create,
            methods=['POST']
        )
        
        # PUT /<resource>/<id> - Update
        self.blueprint.add_url_rule(
            f'/api/{self.name}/<int:id>',
            f'update_{self.name}',
            self.update,
            methods=['PUT']
        )
        
        # DELETE /<resource>/<id> - Delete
        self.blueprint.add_url_rule(
            f'/api/{self.name}/<int:id>',
            f'delete_{self.name}',
            self.delete,
            methods=['DELETE']
        )
    
    def get_all(self):
        """Get all records with pagination and filtering"""
        try:
            page, per_page = get_pagination_args()
            
            # Get search query
            search = request.args.get('q', '')
            
            # Build query
            query = self.model_class.query
            
            # Apply search if search_fields are defined
            if search and hasattr(self.model_class, 'search_fields'):
                search_conditions = []
                for field in self.model_class.search_fields:
                    if hasattr(self.model_class, field):
                        attr = getattr(self.model_class, field)
                        search_conditions.append(attr.ilike(f'%{search}%'))
                
                if search_conditions:
                    query = query.filter(db.or_(*search_conditions))
            
            # Apply filters
            for key, value in request.args.items():
                if key not in ['q', 'page', 'per_page'] and hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
            
            # Apply active filter if available
            if hasattr(self.model_class, 'is_active') and request.args.get('include_inactive') != 'true':
                query = query.filter(self.model_class.is_active == True)
            
            # Get total count
            total = query.count()
            
            # Apply pagination
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            # Convert to dict
            data = [item.to_dict() for item in items]
            
            return ApiResponse.pagination(data, total, page, per_page)
            
        except Exception as e:
            return ApiResponse.error(f"Error retrieving {self.name}: {str(e)}", 500)
    
    @login_required
    def get_by_id(self, id):
        """Get single record by ID"""
        try:
            item = self.model_class.get_by_id(id)
            if not item:
                return ApiResponse.error(f"{self.name.title()} not found", 404)
            
            # Check if user can view this item
            if hasattr(item, 'user_id') and item.user_id != current_user.user_id:
                if not current_user.has_permission(f'manage_{self.permission_prefix}'):
                    return ApiResponse.error("Permission denied", 403)
            
            return ApiResponse.success(item.to_dict(include_relationships=True))
            
        except Exception as e:
            return ApiResponse.error(f"Error retrieving {self.name}: {str(e)}", 500)
    
    @login_required
    @permission_required('manage_{permission_prefix}')
    def create(self):
        """Create new record"""
        try:
            # Validate schema if provided
            if 'create' in self.validation_schemas:
                validate_json_schema_decorator(self.validation_schemas['create'])
            
            data = request.get_json()
            
            # Add user_id if model has user relationship
            if hasattr(self.model_class, 'user_id') and 'user_id' not in data:
                data['user_id'] = current_user.user_id
            
            # Add created_by if model has this field
            if hasattr(self.model_class, 'created_by') and 'created_by' not in data:
                data['created_by'] = current_user.user_id
            
            item = self.model_class.create(**data)
            
            return ApiResponse.success(
                item.to_dict(),
                f"{self.name.title()} created successfully",
                201
            )
            
        except Exception as e:
            return ApiResponse.error(f"Error creating {self.name}: {str(e)}", 400)
    
    @login_required
    def update(self, id):
        """Update existing record"""
        try:
            item = self.model_class.get_by_id(id)
            if not item:
                return ApiResponse.error(f"{self.name.title()} not found", 404)
            
            # Check permissions
            can_update = False
            if hasattr(item, 'user_id') and item.user_id == current_user.user_id:
                can_update = True
            elif current_user.has_permission(f'manage_{self.permission_prefix}'):
                can_update = True
            
            if not can_update:
                return ApiResponse.error("Permission denied", 403)
            
            # Validate schema if provided
            if 'update' in self.validation_schemas:
                validate_json_schema_decorator(self.validation_schemas['update'])
            
            data = request.get_json()
            
            # Remove fields that shouldn't be updated
            protected_fields = ['id', 'created_at', 'user_id', 'created_by']
            for field in protected_fields:
                data.pop(field, None)
            
            item.update(**data)
            
            return ApiResponse.success(
                item.to_dict(),
                f"{self.name.title()} updated successfully"
            )
            
        except Exception as e:
            return ApiResponse.error(f"Error updating {self.name}: {str(e)}", 400)
    
    @login_required
    @permission_required('manage_{permission_prefix}')
    def delete(self, id):
        """Delete record"""
        try:
            item = self.model_class.get_by_id(id)
            if not item:
                return ApiResponse.error(f"{self.name.title()} not found", 404)
            
            # Check if soft delete is preferred
            soft_delete = request.args.get('soft', 'true').lower() == 'true'
            
            item.delete(soft_delete=soft_delete)
            
            return ApiResponse.success(
                None,
                f"{self.name.title()} deleted successfully"
            )
            
        except Exception as e:
            return ApiResponse.error(f"Error deleting {self.name}: {str(e)}", 500)

def create_crud_blueprint(name, model_class, **kwargs):
    """Factory function to create CRUD blueprint"""
    crud = CRUDBlueprint(name, model_class, **kwargs)
    return crud.blueprint

# Usage example:
"""
from models.book import Book

book_schemas = {
    'create': {
        'type': 'object',
        'required': ['title', 'isbn'],
        'properties': {
            'title': {'type': 'string', 'maxLength': 255},
            'isbn': {'type': 'string', 'maxLength': 20},
            'description': {'type': 'string'}
        }
    },
    'update': {
        'type': 'object',
        'properties': {
            'title': {'type': 'string', 'maxLength': 255},
            'description': {'type': 'string'}
        }
    }
}

books_bp = create_crud_blueprint('books', Book, validation_schemas=book_schemas)
app.register_blueprint(books_bp)
"""
