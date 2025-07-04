from flask import Blueprint, request, jsonify, abort
from services.ticket_service import search_tickets_service
from services.ticket_service import get_ticket_details_service
from services.ticket_service import check_cancellation_penalty_service
import logging
from services.ticket_service import cancel_ticket_and_refund_service
from functools import wraps
ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/search', methods=['GET'])
def search_tickets():
    args = request.args

    origin_id = args.get('origin_id', type=int)
    destination_id = args.get('destination_id', type=int)
    travel_date = args.get('travel_date')  # Expect 'YYYY-MM-DD'
    vehicle_type = args.get('vehicle_type')  # 'plane', 'train', 'bus' or None
    min_price = args.get('min_price', type=float)
    max_price = args.get('max_price', type=float)
    company_name = args.get('company_name')
    departure_start = args.get('departure_start')  # 'HH:MM'
    departure_end = args.get('departure_end')      # 'HH:MM'
    travel_class = args.get('travel_class', type=int)

    # Basic validation
    if not origin_id or not destination_id or not travel_date:
        return jsonify({'status': 'error', 'message': 'origin_id, destination_id and travel_date are required'}), 400

    results = search_tickets_service(
        origin_id, destination_id, travel_date, vehicle_type,
        min_price, max_price, company_name,
        departure_start, departure_end, travel_class
    )

    return jsonify({'status': 'success', 'tickets': results})

@ticket_bp.route('/details/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    ticket = get_ticket_details_service(ticket_id)
    if not ticket:
        return jsonify({'status': 'error', 'message': 'Ticket not found'}), 404
    return jsonify({'status': 'success', 'ticket': ticket})

@ticket_bp.route('/cancel/check/<int:ticket_id>', methods=['GET'])
def check_cancellation_penalty(ticket_id):
    try:
        penalty_info = check_cancellation_penalty_service(ticket_id)
        return jsonify(penalty_info), 200
    except ValueError as e:
        # Handle specific errors from the service layer
        if "not found" in str(e).lower():
            return jsonify({"status": "error", "message": str(e)}), 404
        else:
            return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        # Handle unexpected server errors
        logging.error(f"Error checking cancellation penalty for ticket {ticket_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500



####################################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real app, you would decode a JWT here to get the user's ID.
        # For testing, we will hardcode a user_id.
        user_id = 2  # Example user_id.
        logging.info(f"Simulating login for user_id: {user_id}")
        
        # We pass the user_id as a new keyword argument to the decorated function
        return f(current_user_id=user_id, *args, **kwargs)
    return decorated_function


# --- Your existing ticket routes would be here ---
# Example:
# @ticket_bp.route('/search', methods=['GET'])
# def search_tickets():
#     # ... your ticket search logic ...
#     pass


# @ticket_bp.route('/cancel/check/<int:ticket_id>', methods=['GET'])
# def check_cancellation_penalty(ticket_id):
#     """
#     Checks the cancellation penalty for a specific ticket.
#     """
#     try:
#         penalty_info = check_cancellation_penalty_service(ticket_id)
#         return jsonify(penalty_info), 200
#     except ValueError as e:
#         if "not found" in str(e).lower():
#             return jsonify({"status": "error", "message": str(e)}), 404
#         else:
#             return jsonify({"status": "error", "message": str(e)}), 400
#     except Exception as e:
#         logging.error(f"Error checking cancellation penalty for ticket {ticket_id}: {e}")
#         return jsonify({"status": "error", "message": "An internal error occurred."}), 500


@ticket_bp.route('/cancel/<int:ticket_id>', methods=['POST'])
@login_required # This will now work correctly
def cancel_ticket(current_user_id, ticket_id):
    """
    Finalizes the cancellation of a ticket and processes the refund.
    """
    try:
        result = cancel_ticket_and_refund_service(current_user_id, ticket_id)
        return jsonify({"status": "success", "data": result}), 200
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403 # Forbidden
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400 # Bad Request
    except Exception as e:
        logging.error(f"Error cancelling ticket {ticket_id} for user {current_user_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred during cancellation."}), 500

