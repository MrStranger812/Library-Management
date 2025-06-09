from flask_login import login_required
from models.author import Author
from routes.generic_crud_routes import CRUDBlueprint

# Create the authors blueprint with CRUD functionality
authors_crud = CRUDBlueprint(
    name='authors',
    model_class=Author,
    permission_prefix='authors',
    validation_schemas={
        'create': {
            'type': 'object',
            'required': ['first_name', 'last_name'],
            'properties': {
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'biography': {'type': 'string'},
                'birth_date': {'type': 'string', 'format': 'date'},
                'death_date': {'type': 'string', 'format': 'date'},
                'nationality': {'type': 'string'}
            }
        },
        'update': {
            'type': 'object',
            'properties': {
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'biography': {'type': 'string'},
                'birth_date': {'type': 'string', 'format': 'date'},
                'death_date': {'type': 'string', 'format': 'date'},
                'nationality': {'type': 'string'}
            }
        }
    }
)

# Export the blueprint
authors_bp = authors_crud.blueprint 