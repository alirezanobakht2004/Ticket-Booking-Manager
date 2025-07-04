# api/payment.py

from flask import Blueprint, request, jsonify
# --- CHANGE 1: Import the correct function name ---
from services.payment_service import process_payment_for_ticket_service
import logging



payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pay/ticket/<int:ticket_id>', methods=['POST'])
def pay_for_ticket(ticket_id):
    """
    Processes payment for a ticket by finding its reservation and
    paying for the entire reservation.
    """
    data = request.get_json()
    payment_method = data.get('payment_method')

    if not payment_method:
        return jsonify({'status': 'error', 'message': 'payment_method is required'}), 400

    try:

        # --- CHANGE 2: Simplified to call the single service function ---
        # The service now handles all logic internally (finding reservation, etc.)


        finalized_tickets = process_payment_for_ticket_service(
            ticket_id=ticket_id,
            payment_method=payment_method
        )

        return jsonify({
            'status': 'success',
            'message': 'Payment successful. Reservation confirmed.',
            'ticket_details': finalized_tickets
        })

    except ValueError as e:
        # For validation errors like "Reservation expired"
        return jsonify({'status': 'error', 'message': str(e)}), 404
    except Exception as e:
        # For internal server errors
        logging.error(f"Payment processing error initiated by ticket {ticket_id}: {e}")
        return jsonify({'status': 'error', 'message': 'Payment processing failed'}), 500

