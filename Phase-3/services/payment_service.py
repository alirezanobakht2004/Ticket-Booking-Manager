# services/payment_service.py

import logging
from datetime import datetime
import uuid

from db.db import (
    get_reservation_by_id,
    get_total_amount_for_reservation,
    create_payment_record,
    update_reservation_status,
    get_finalized_ticket_details,
    find_reservation_by_ticket_id  # Keep this if you need it for other functions
)

def process_payment_for_reservation_service(reservation_id: int, passenger_id: int, payment_method: str):
    """
    Processes payment for a specific reservation owned by passenger_id.
    Validates ownership, status, and expiry, then records payment
    and marks reservation CONFIRMED. Returns finalized ticket details.
    """
    # 1. Get reservation by ID
    reservation = get_reservation_by_id(reservation_id)
    if not reservation:
        raise ValueError(f"Reservation not found: {reservation_id}")

    # 2. Ownership check (your reservation table uses passenger_id == person_id)
    if reservation.get('passenger_id') != passenger_id:
        raise ValueError("You do not have permission to pay for this reservation.")

    # 3. Validate reservation status
    status = reservation.get('status')
    if status == 'CONFIRMED':
        raise ValueError("This reservation has already been paid for.")
    if status not in ('active', 'PENDING'):
        raise ValueError(f"Reservation is not in a payable state. Current status: {status}")

    # 4. Check expiry time
    expiry_time = reservation.get('expiry_time')
    if expiry_time and datetime.utcnow() > expiry_time:
        raise ValueError("This reservation has expired and can no longer be paid.")

    # 5. Calculate total amount
    total_amount = get_total_amount_for_reservation(reservation_id)
    if not total_amount or total_amount <= 0:
        raise ValueError("Cannot process payment for a zero or negative amount.")

    # 6. Simulate payment gateway
    logging.info(f"Simulating payment of {total_amount} for reservation {reservation_id} via {payment_method}")
    transaction_ref = f"txn_{uuid.uuid4()}"

    # 7. Record transaction
    create_payment_record(
        reservation_id=reservation_id,
        amount=total_amount,
        method=payment_method,
        status='SUCCESSFUL',
        transaction_ref=transaction_ref
    )

    # 8. Mark reservation confirmed
    update_reservation_status(reservation_id, 'CONFIRMED')

    # 9. Return issued ticket details
    return get_finalized_ticket_details(reservation_id)

# Keep your existing function for ticket-based payments
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
        raise ValueError("This reservation has expired and can no longer be paid.")

    reservation_id = reservation['reservation_id']

    # 3. Calculate the total amount
    total_amount = get_total_amount_for_reservation(reservation_id)
    if total_amount <= 0:
        raise ValueError("Cannot process payment for a zero or negative amount.")

    # 4. Simulate payment gateway interaction
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