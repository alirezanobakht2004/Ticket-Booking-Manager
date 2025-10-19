# api/report.py

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from services.report_service import submit_report_service

report_bp = Blueprint('report', __name__)

# --- Placeholder for User Authentication ---
# This should be the same decorator used in your other user-facing APIs
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # For testing, we hardcode a user_id.
        user_id = 2  # Example user_id.
        logging.info(f"Simulating login for user_id: {user_id}")
        return f(current_user_id=user_id, *args, **kwargs)
    return decorated_function


@report_bp.route('/submit', methods=['POST'])
@login_required
def submit_report(current_user_id):
    """
    Submits a new issue report for a ticket.
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Request body is required."}), 400

    ticket_id = data.get('ticket_id')
    report_type = data.get('report_type')
    report_text = data.get('report_text')

    if not all([ticket_id, report_type, report_text]):
        return jsonify({"status": "error", "message": "ticket_id, report_type, and report_text are required."}), 400

    try:
        result = submit_report_service(current_user_id, ticket_id, report_type, report_text)
        return jsonify({"status": "success", "data": result}), 201 # 201 Created
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403 # Forbidden
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400 # Bad Request
    except Exception as e:
        logging.error(f"Error submitting report for user {current_user_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500
