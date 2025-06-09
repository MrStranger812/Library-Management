from flask import Blueprint, jsonify, request, render_template
from models.reports import Reports
from utils.security import permission_required
from utils.error_handler import handle_error

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@permission_required('admin')
def index():
    """Render the reports management page."""
    return render_template('reports/index.html')

@reports_bp.route('/reports', methods=['GET'])
@permission_required('admin')
@handle_error
def get_reports():
    """Get all reports."""
    reports = Reports.query.all()
    return jsonify([report.to_dict() for report in reports])

@reports_bp.route('/reports/<int:report_id>', methods=['GET'])
@permission_required('admin')
@handle_error
def get_report(report_id):
    """Get a specific report."""
    report = Reports.query.get_or_404(report_id)
    return jsonify(report.to_dict()) 