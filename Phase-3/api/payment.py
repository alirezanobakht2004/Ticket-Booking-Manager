# api/payment.py

from flask import Blueprint, request, jsonify
from services.payment_service import process_payment_for_ticket_service
import logging

# The Blueprint name is 'payment'. It will be registered in app.py
# with the prefix '/api/payments'.
payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pay/ticket/<int:ticket_id>', methods=['POST'])
def pay_for_ticket(ticket_id):
    """
    Processes payment for all tickets within a reservation,
    identified by a single ticket_id.
    """
    # --- CHANGE 1: More robust check for request body ---
    # This ensures the request has a JSON body and the required field.
    data = request.get_json()
    if not data or 'payment_method' not in data:
        return jsonify({'status': 'error', 'message': 'payment_method is required in the request body'}), 400

    payment_method = data['payment_method']

    try:
        # The call to the service layer is correct.
        finalized_tickets = process_payment_for_ticket_service(
            ticket_id=ticket_id,
            payment_method=payment_method
        )

        # --- CHANGE 2: Explicitly return 200 OK on success ---
        return jsonify({
            'status': 'success',
            'message': 'Payment successful. Reservation confirmed.',
            'ticket_details': finalized_tickets
        }), 200

    except ValueError as e:
        # --- CHANGE 3: More specific error handling ---
        # We now check the error message to return the correct HTTP status code.
        # 404 for "Not Found" errors, and 400 for other client-side validation errors.
        if "No reservation found" in str(e):
             return jsonify({'status': 'error', 'message': str(e)}), 404
        else:
             # For errors like "Reservation expired" or "Already paid"
             return jsonify({'status': 'error', 'message': str(e)}), 400

    except Exception as e:
        # This catches unexpected internal errors.
        logging.error(f"An unexpected error occurred during payment for ticket {ticket_id}: {e}")
        # --- CHANGE 4: More generic message for internal errors ---
        # It's safer not to expose exact internal error details to the client.
        return jsonify({'status': 'error', 'message': 'An internal error occurred during payment processing.'}), 500
