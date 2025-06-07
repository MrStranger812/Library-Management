from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.fine import Fine
from utils.security import Security
from utils.middleware import validate_json_schema

fines_bp = Blueprint('fines', __name__)

@fines_bp.route('/api/fines', methods=['GET'])
@login_required
def get_fines():
    fines = Fine.get_all()
    return jsonify([fine.to_dict() for fine in fines])

@fines_bp.route('/api/fines/<int:fine_id>', methods=['GET'])
@login_required
def get_fine(fine_id):
    fine = Fine.get_by_id(fine_id)
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404
    return jsonify(fine.to_dict())

@fines_bp.route('/api/fines/<int:fine_id>/pay', methods=['POST'])
@login_required
def pay_fine(fine_id):
    fine = Fine.get_by_id(fine_id)
    if not fine:
        return jsonify({'error': 'Fine not found'}), 404
    try:
        fine.pay()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400 