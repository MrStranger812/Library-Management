from flask_login import login_required
from models.library_event import LibraryEvent
from routes.generic_crud_routes import CRUDBlueprint

# Create the events blueprint with CRUD functionality
events_crud = CRUDBlueprint(
    name='events',
    model_class=LibraryEvent,
    permission_prefix='events',
    validation_schemas={
        'create': {
            'type': 'object',
            'required': ['title', 'event_type', 'start_time', 'end_time'],
            'properties': {
                'title': {'type': 'string'},
                'description': {'type': 'string'},
                'event_type': {'type': 'string'},
                'start_time': {'type': 'string', 'format': 'date-time'},
                'end_time': {'type': 'string', 'format': 'date-time'},
                'location': {'type': 'string'},
                'capacity': {'type': 'integer', 'minimum': 1},
                'registration_deadline': {'type': 'string', 'format': 'date-time'}
            }
        },
        'update': {
            'type': 'object',
            'properties': {
                'title': {'type': 'string'},
                'description': {'type': 'string'},
                'event_type': {'type': 'string'},
                'start_time': {'type': 'string', 'format': 'date-time'},
                'end_time': {'type': 'string', 'format': 'date-time'},
                'location': {'type': 'string'},
                'capacity': {'type': 'integer', 'minimum': 1},
                'registration_deadline': {'type': 'string', 'format': 'date-time'}
            }
        }
    }
)

# Export the blueprint
events_bp = events_crud.blueprint 