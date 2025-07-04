from db.db import search_tickets
from services.cache_service import get_cached_search, cache_search
import hashlib
import json
from db.db import get_ticket_details
from datetime import datetime, timedelta
from db.db import get_ticket_for_cancellation_check
from db.db import get_ticket_owner_person_id, add_to_user_wallet, update_reservation_status, get_reservation_by_ticket_id

def generate_cache_key(params: dict) -> str:
    key_str = json.dumps(params, sort_keys=True)
    return "search_tickets:" + hashlib.md5(key_str.encode()).hexdigest()

import datetime

def serialize_datetimes(obj):
    if isinstance(obj, list):
        return [serialize_datetimes(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: (v.isoformat() if isinstance(v, datetime.datetime) else serialize_datetimes(v)) for k, v in obj.items()}
    else:
        return obj

def search_tickets_service(
    origin_id,
    destination_id,
    travel_date,
    vehicle_type=None,
    min_price=None,
    max_price=None,
    company_name=None,
    departure_start=None,
    departure_end=None,
    travel_class=None
):
    params = {
        "origin_id": origin_id,
        "destination_id": destination_id,
        "travel_date": travel_date,
        "vehicle_type": vehicle_type,
        "min_price": min_price,
        "max_price": max_price,
        "company_name": company_name,
        "departure_start": departure_start,
        "departure_end": departure_end,
        "travel_class": travel_class
    }

    cache_key = generate_cache_key(params)
    cached_result = get_cached_search(cache_key)
    if cached_result is not None:
        return cached_result

    results = search_tickets(
        origin_id=origin_id,
        destination_id=destination_id,
        travel_date=travel_date,
        vehicle_type=vehicle_type,
        min_price=min_price,
        max_price=max_price,
        company_name=company_name,
        departure_start=departure_start,
        departure_end=departure_end,
        travel_class=travel_class
    )

    # Serialize datetime objects before caching
    results_serializable = serialize_datetimes(results)

    cache_search(cache_key, results_serializable)
    return results_serializable



def get_ticket_details_service(ticket_id):
    ticket = get_ticket_details(ticket_id)
    if not ticket:
        return None
    # Optionally, compute remaining capacity
    remaining_capacity = ticket['capacity'] - ticket['reserved_number'] if ticket['capacity'] is not None else None
    ticket['remaining_capacity'] = remaining_capacity
    return ticket



def check_cancellation_penalty_service(ticket_id: int):
    """
    Checks the cancellation penalty for a given ticket without performing the cancellation.
    """
    ticket = get_ticket_for_cancellation_check(ticket_id)

    if not ticket:
        raise ValueError("Ticket not found.")

    if ticket['reservation_status'] != 'CONFIRMED':
        raise ValueError(f"Ticket is not in a cancellable state. Current status: {ticket['reservation_status']}")

    # The call to utcnow() will now work correctly.
    now_utc = datetime.datetime.utcnow()
    if now_utc >= ticket['departure_time']:
        raise ValueError("This ticket cannot be cancelled as the departure time has passed.")

    time_remaining = ticket['departure_time'] - now_utc
    hours_remaining = time_remaining.total_seconds() / 3600

    penalty_percentage = 0
    vehicle_type = ticket['vehicle_type']
    
    # --- EXAMPLE CANCELLATION RULES ---
    if vehicle_type == 'plane':
        if hours_remaining > 24:
            penalty_percentage = 10
        elif 12 <= hours_remaining <= 24:
            penalty_percentage = 30
        else: # Less than 12 hours
            penalty_percentage = 50
    elif vehicle_type in ['bus', 'train']:
        if hours_remaining > 8:
            penalty_percentage = 5
        elif 3 <= hours_remaining <= 8:
            penalty_percentage = 15
        else: # Less than 3 hours
            penalty_percentage = 40
    else: # Unknown vehicle type
        penalty_percentage = 100
    
    ticket_price = ticket['price']
    penalty_amount = (ticket_price * penalty_percentage) / 100
    refundable_amount = ticket_price - penalty_amount

    return {
        "ticket_id": ticket_id,
        "ticket_price": float(ticket_price), # Ensure price is a float
        "departure_time": ticket['departure_time'].isoformat() + "Z",
        "hours_remaining": round(hours_remaining, 2),
        "penalty_percentage": penalty_percentage,
        "penalty_amount": round(penalty_amount, 2),
        "refundable_amount": round(refundable_amount, 2)
    }


###########################################


def cancel_ticket_and_refund_service(current_user_id: int, ticket_id: int):
    """
    Handles the full process of cancelling a ticket and refunding the user.
    """
    # Step 1: Verify that the current user is the owner of the ticket.
    ticket_owner_id = get_ticket_owner_person_id(ticket_id)
    if not ticket_owner_id or ticket_owner_id != current_user_id:
        raise PermissionError("You do not have permission to cancel this ticket.")

    # Step 2: Get penalty info. This also re-validates the ticket's status and departure time.
    # The `check_cancellation_penalty_service` will raise a ValueError if the ticket is not cancellable.
    try:
        penalty_info = check_cancellation_penalty_service(ticket_id)
        refundable_amount = penalty_info['refundable_amount']
    except ValueError as e:
        # Re-raise the error with a more specific message for this context
        raise ValueError(f"Ticket cancellation failed: {str(e)}") from e

    # Step 3: Find the reservation_id associated with the ticket
    reservation = get_reservation_by_ticket_id(ticket_id)
    if not reservation:
        raise ValueError("Could not find reservation for this ticket.")
    
    reservation_id = reservation['reservation_id']

    # Step 4: Update the reservation status to 'CANCELLED'
    if not update_reservation_status(reservation_id, 'CANCELLED'):
        raise Exception("Failed to update reservation status.")

    # Step 5: Add the refundable amount to the user's wallet
    if refundable_amount > 0:
        if not add_to_user_wallet(current_user_id, refundable_amount):
            # This is a critical error. The reservation is cancelled but the user was not refunded.
            # This should be logged for manual intervention by an admin.
            logging.critical(f"CRITICAL: User {current_user_id} was not refunded {refundable_amount} for cancelled reservation {reservation_id}.")
            raise Exception("Cancellation was successful, but a refund processing error occurred. Please contact support.")

    return {
        "message": "Ticket cancelled successfully.",
        "reservation_id": reservation_id,
        "refunded_amount": refundable_amount
    }