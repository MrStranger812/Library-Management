"""
Routes for managing library fines.
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from models.fine import Fine
from models.fine_payment import FinePayment
from utils.security import Security, permission_required
from utils.validation import validate_json_schema_decorator
from utils.error_handler import handle_error

fines_bp = Blueprint('fines', __name__)

@fines_bp.route('/api/fines', methods=['GET'])
@login_required
def get_fines():
    """Get all fines."""
    if current_user.role in ['admin', 'librarian']:
        fines = Fine.get_all()
    else:
        fines = Fine.get_user_fines(current_user.user_id)
    return jsonify([fine.to_dict() for fine in fines])

@fines_bp.route('/api/fines/<int:fine_id>', methods=['GET'])
@login_required
def get_fine(fine_id):
    """Get a specific fine."""
    fine = Fine.get_by_id(fine_id)
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404
    
    # Check if user has permission to view this fine
    if current_user.role not in ['admin', 'librarian'] and fine.borrowing.user_id != current_user.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(fine.to_dict())

@fines_bp.route('/api/fines/<int:fine_id>/pay', methods=['POST'])
@login_required
@validate_json_schema_decorator({
    'type': 'object',
    'properties': {
        'amount': {'type': 'number', 'minimum': 0},
        'payment_method': {'type': 'string', 'enum': ['cash', 'credit_card', 'debit_card', 'online']},
        'reference_number': {'type': 'string'},
        'notes': {'type': 'string'}
    },
    'required': ['amount']
})
def pay_fine(fine_id):
    """Pay a fine."""
    fine = Fine.get_by_id(fine_id)
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404
    
    # Check if user has permission to pay this fine
    if current_user.role not in ['admin', 'librarian'] and fine.borrowing.user_id != current_user.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    try:
        data = request.get_json()
        fine.pay(
            amount=data.get('amount'),
            payment_method=data.get('payment_method', 'cash'),
            reference_number=data.get('reference_number'),
            notes=data.get('notes')
        )
        return jsonify(fine.to_dict())
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'An error occurred while processing the payment'}), 500

@fines_bp.route('/api/fines/pending', methods=['GET'])
@login_required
def get_pending_fines():
    """Get all pending fines."""
    if current_user.role not in ['admin', 'librarian']:
        return jsonify({'error': 'Permission denied'}), 403
    
    fines = Fine.get_pending_fines()
    return jsonify([fine.to_dict() for fine in fines])

@fines_bp.route('/api/fines/user/<int:user_id>', methods=['GET'])
@login_required
def get_user_fines(user_id):
    """Get all fines for a specific user."""
    if current_user.role not in ['admin', 'librarian'] and current_user.user_id != user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    fines = Fine.get_user_fines(user_id)
    return jsonify([fine.to_dict() for fine in fines])

@fines_bp.route('/fines', methods=['POST'])
@validate_json_schema_decorator({
    'type': 'object',
    'required': ['borrowing_id', 'amount'],
    'properties': {
        'borrowing_id': {'type': 'integer'},
        'amount': {'type': 'number', 'minimum': 0},
        'reason': {'type': 'string'}
    }
})
def create_fine():
    data = request.get_json()
    fine = Fine(**data)
    db.session.add(fine)
    db.session.commit()
    return jsonify(fine.to_dict()), 201

@fines_bp.route('/fines')
@permission_required('admin')
def index():
    """Render the fines management page."""
    return render_template('fines/index.html') 