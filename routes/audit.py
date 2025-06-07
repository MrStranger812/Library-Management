from flask import Blueprint, jsonify
from flask_login import login_required
from models.audit_log import AuditLog
from utils.security import permission_required

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/audit-logs', methods=['GET'])
@login_required
@permission_required('view_audit_logs')
def get_audit_logs():
    logs = AuditLog.query.all()
    return jsonify([log.to_dict() for log in logs])

@audit_bp.route('/api/audit-logs/<int:log_id>', methods=['GET'])
@login_required
@permission_required('view_audit_logs')
def get_audit_log(log_id):
    log = AuditLog.get_by_id(log_id)
    if not log:
        return jsonify({'error': 'Log not found'}), 404
    return jsonify(log.to_dict()) 