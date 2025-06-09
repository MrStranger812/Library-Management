from flask import render_template, jsonify
from models.reports import Reports
from utils.security import permission_required
from utils.error_handler import handle_error
from routes.generic_crud_routes import CRUDBlueprint

# Create the reports blueprint with CRUD functionality
reports_crud = CRUDBlueprint(
    name='reports',
    model_class=Reports,
    permission_prefix='admin'  # All report operations require admin permission
)

# Add custom routes
@reports_crud.blueprint.route('/reports')
@permission_required('admin')
def index():
    """Render the reports management page."""
    return render_template('reports/index.html')

# Export the blueprint
reports_bp = reports_crud.blueprint

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