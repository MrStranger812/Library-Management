from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.borrowing import Borrowing
from utils.security import permission_required
from utils.middleware import validate_json_schema

borrowings_bp = Blueprint('borrowings', __name__)

@borrowings_bp.route('/api/borrowings/borrow', methods=['POST'])
@login_required
@validate_json_schema({
    'type': 'object',
    'required': ['book_id'],
    'properties': {
        'book_id': {'type': 'integer'},
        'days': {'type': 'integer', 'minimum': 1, 'maximum': 30}
    }
})
def borrow_book():
    data = request.get_json()
    
    try:
        borrowing = Borrowing.create(
            user_id=current_user.user_id,
            book_id=data['book_id'],
            days=data.get('days', 14)
        )
        return jsonify({'success': True, 'borrowing_id': borrowing.borrowing_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@borrowings_bp.route('/api/borrowings/return', methods=['POST'])
@login_required
@permission_required('manage_borrowings')
@validate_json_schema({
    'type': 'object',
    'required': ['borrowing_id'],
    'properties': {
        'borrowing_id': {'type': 'integer'}
    }
})
def return_book():
    data = request.get_json()
    
    try:
        borrowing = Borrowing.get_by_id(data['borrowing_id'])
        if not borrowing:
            return jsonify({'success': False, 'message': 'Borrowing record not found'}), 404
        
        if borrowing.user_id != current_user.user_id and not current_user.has_permission('manage_borrowings'):
            return jsonify({'success': False, 'message': 'Permission denied'}), 403
        
        borrowing.return_book()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@borrowings_bp.route('/api/borrowings/user', methods=['GET'])
@login_required
def get_user_borrowings():
    borrowings = Borrowing.get_by_user(current_user.user_id)
    return jsonify([borrowing.to_dict() for borrowing in borrowings])

@borrowings_bp.route('/api/borrowings/overdue', methods=['GET'])
@login_required
@permission_required('manage_borrowings')
def get_overdue_borrowings():
    borrowings = Borrowing.get_overdue()
    return jsonify([borrowing.to_dict() for borrowing in borrowings]) 