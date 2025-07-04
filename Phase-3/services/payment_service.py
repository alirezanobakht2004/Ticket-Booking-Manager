# services/payment_service.py

import logging
from datetime import datetime
import uuid

# Import the new DB functions you just added
from db.db import (
    find_reservation_by_ticket_id,
    get_total_amount_for_reservation,
    create_payment_record,
    update_reservation_status,
    get_finalized_ticket_details
)

def process_payment_for_ticket_service(ticket_id: int, payment_method: str):
    """
    Service to process a payment for a reservation linked to a ticket.
    """
    # 1. Find the reservation using the ticket ID
    reservation = find_reservation_by_ticket_id(ticket_id)

    if not reservation:
        raise ValueError(f"No reservation found for ticket ID: {ticket_id}")

    # 2. Validate the reservation status and expiry
    if reservation['status'] == 'CONFIRMED':
        raise ValueError("This reservation has already been paid for.")

    if reservation['status'] != 'PENDING':
         raise ValueError(f"Reservation is not in a payable state. Current status: {reservation['status']}")

    if datetime.utcnow() > reservation['expiry_time']:
        # Optionally, you could also update the status to 'EXPIRED' here
        # update_reservation_status(reservation['reservation_id'], 'EXPIRED')
        raise ValueError("This reservation has expired and can no longer be paid.")

    reservation_id = reservation['reservation_id']

    # 3. Calculate the total amount
    total_amount = get_total_amount_for_reservation(reservation_id)
    if total_amount <= 0:
        raise ValueError("Cannot process payment for a zero or negative amount.")

    # 4. Simulate payment gateway interaction
    # In a real application, you would integrate with a payment provider here.
    # For now, we'll assume the payment is always successful.
    logging.info(f"Simulating payment of {total_amount} for reservation {reservation_id} via {payment_method}")
    payment_successful = True
    transaction_ref = f"txn_{uuid.uuid4()}"

    # 5. Record the transaction and update statuses
    if payment_successful:
        # Create a record in the payment table
        create_payment_record(
            reservation_id=reservation_id,
            amount=total_amount,
            method=payment_method,
            status='SUCCESSFUL',
            transaction_ref=transaction_ref
        )

        # Update the reservation status to 'CONFIRMED'
        update_reservation_status(reservation_id, 'CONFIRMED')
        
        # NOTE: You might also want a status on the ticket table itself.
        # If so, you would create and call a db function here to update all tickets
        # with the reservation_id to a status like 'ISSUED'.

        # 6. Return the finalized ticket details
        finalized_tickets = get_finalized_ticket_details(reservation_id)
        return finalized_tickets
    else:
        # Handle payment failure
        create_payment_record(
            reservation_id=reservation_id,
            amount=total_amount,
            method=payment_method,
            status='FAILED',
            transaction_ref=transaction_ref
        )
        raise Exception("Payment gateway failed to process the transaction.")