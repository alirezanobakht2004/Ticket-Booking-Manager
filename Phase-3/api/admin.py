# api/admin.py

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from services.admin_service import list_reservations_service, list_reports_service, update_reservation_status_by_admin_service
from services.admin_service import list_payments_by_status_service, get_reservation_details_for_admin_service

admin_bp = Blueprint('admin', __name__)

# --- FIX: The function definition is now UNCOMMENTED ---
# This decorator will now exist and can be used on your routes.
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # EXAMPLE LOGIC: Check for a specific header or a user role from a JWT token.
        # For now, we will just log a warning. In production, this must be a real check.
        logging.warning("Admin access check is not implemented! Allowing request.")
        # if not is_admin_user(request):
        #     return jsonify({"status": "error", "message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/reservations', methods=['GET'])
@admin_required
def get_reservations_by_filter():
    """Admin endpoint to get reservations filtered by status."""
    status = request.args.get('status') # e.g., ?status=CANCELLED
    if not status:
        return jsonify({"status": "error", "message": "Query parameter 'status' is required."}), 400
        
    try:
        reservations = list_reservations_service(status)
        return jsonify(reservations), 200
    except Exception as e:
        logging.error(f"Admin error fetching reservations: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500


@admin_bp.route('/reservations/<int:reservation_id>/status', methods=['POST'])
@admin_required
def update_reservation_status_admin(reservation_id):
    """Admin endpoint to manually update a reservation's status."""
    data = request.get_json()
    if not data or 'new_status' not in data:
        return jsonify({"status": "error", "message": "new_status is required in the request body."}), 400

    new_status = data['new_status']
    
    try:
        result = update_reservation_status_by_admin_service(reservation_id, new_status)
        return jsonify({"status": "success", "data": result}), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logging.error(f"Admin error updating reservation {reservation_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500

@admin_bp.route('/reports', methods=['GET'])
@admin_required
def get_reports():
    """Admin endpoint to get all user reports."""
    try:
        reports = list_reports_service()
        return jsonify(reports), 200
    except Exception as e:
        logging.error(f"Admin error fetching reports: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500


###################################
@admin_bp.route('/payments', methods=['GET'])
@admin_required
def get_payments_by_filter():
    """Admin endpoint to get payments filtered by status (e.g., FAILED, SUCCESSFUL)."""
    status = request.args.get('status')
    if not status:
        return jsonify({"status": "error", "message": "Query parameter 'status' is required."}), 400
        
    try:
        payments = list_payments_by_status_service(status)
        return jsonify(payments), 200
    except Exception as e:
        logging.error(f"Admin error fetching payments: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500


@admin_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
@admin_required
def get_single_reservation_details(reservation_id):
    """Admin endpoint to get all details for a single reservation, including its tickets."""
    try:
        details = get_reservation_details_for_admin_service(reservation_id)
        return jsonify(details), 200
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logging.error(f"Admin error fetching reservation details for {reservation_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500