from flask import current_app, request, abort
from jsonschema import validate, ValidationError
from functools import wraps

def validate_json_schema(schema):
    """
    Validate request JSON against a JSON Schema.
    
    Args:
        schema (dict): The JSON Schema to validate against
        
    Raises:
        ValidationError: If the JSON is invalid according to the schema
    """
    if not request.is_json:
        raise ValidationError("Request must be JSON")
        
    try:
        validate(instance=request.get_json(), schema=schema)
    except ValidationError as e:
        raise ValidationError(f"Invalid JSON: {str(e)}")

def validate_json_schema_decorator(schema):
    """
    Decorator to validate request JSON against a JSON Schema.
    
    Args:
        schema (dict): The JSON Schema to validate against
        
    Returns:
        function: Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                validate_json_schema(schema)
            except ValidationError as e:
                abort(400, str(e))
            return f(*args, **kwargs)
        return decorated_function
    return decorator 