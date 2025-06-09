from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.library_event import LibraryEvent
from utils.security import permission_required
from utils.validation import validate_json_schema_decorator

events_bp = Blueprint('events', __name__)

@events_bp.route('/api/events', methods=['GET'])
def get_events():
    events = LibraryEvent.get_all()
    return jsonify([event.to_dict() for event in events])

@events_bp.route('/api/events', methods=['POST'])
@login_required
@permission_required('manage_events')
@validate_json_schema_decorator({
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
})
def add_event():
    data = request.get_json()
    try:
        event = LibraryEvent.create(**data)
        return jsonify({'success': True, 'event_id': event.event_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
@permission_required('manage_events')
@validate_json_schema_decorator({
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
})
def update_event(event_id):
    event = LibraryEvent.get_by_id(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    data = request.get_json()
    try:
        event.update(**data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@events_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
@permission_required('manage_events')
def delete_event(event_id):
    event = LibraryEvent.get_by_id(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    try:
        event.delete()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400 