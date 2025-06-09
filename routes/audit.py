from flask import Blueprint, jsonify, request
from models.notification import AuditLog
from utils.security import permission_required
from utils.error_handler import handle_error

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit-logs', methods=['GET'])
@permission_required('admin')
@handle_error
def get_audit_logs():
    """Get all audit logs."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page
    })

@audit_bp.route('/audit-logs/<int:log_id>', methods=['GET'])
@permission_required('admin')
@handle_error
def get_audit_log(log_id):
    """Get a specific audit log."""
    log = AuditLog.query.get_or_404(log_id)
    return jsonify(log.to_dict())

@audit_bp.route('/audit-logs/user/<int:user_id>', methods=['GET'])
@permission_required('admin')
@handle_error
def get_user_audit_logs(user_id):
    """Get audit logs for a specific user."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    logs = AuditLog.query.filter_by(user_id=user_id).order_by(
        AuditLog.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': logs.page
    }) 