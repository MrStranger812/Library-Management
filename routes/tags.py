from flask_login import login_required
from models.tag import Tag
from routes.generic_crud_routes import CRUDBlueprint

# Create the tags blueprint with CRUD functionality
tags_crud = CRUDBlueprint(
    name='tags',
    model_class=Tag,
    permission_prefix='tags',
    validation_schemas={
        'create': {
            'type': 'object',
            'required': ['name'],
            'properties': {
                'name': {'type': 'string'},
                'color': {'type': 'string'}
            }
        }
    }
)

# Export the blueprint
tags_bp = tags_crud.blueprint 