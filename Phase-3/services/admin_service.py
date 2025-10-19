from db.db import get_reservations_by_status, get_all_reports, get_reservation_by_id, update_reservation_status,get_full_reservation_details,get_payments_by_status
import logging

def list_reservations_service(status):
    """
    Service to list reservations based on their status.
    """
    if not status:
        raise ValueError("Status parameter is required.")
    
    reservations = get_reservations_by_status(status)
    return reservations

def list_reports_service():
    """
    Service to list all user reports.
    """
    reports = get_all_reports()
    return reports

def update_reservation_status_by_admin_service(reservation_id, new_status):
    """
    Service for an admin to update the status of a reservation.
    """
    # Check if the reservation exists
    reservation = get_reservation_by_id(reservation_id)
    if not reservation:
        raise ValueError("Reservation not found.")
        
    # A list of valid statuses an admin can set.
    valid_statuses = ['CONFIRMED', 'CANCELLED', 'PENDING']
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status provided. Must be one of {valid_statuses}")

    # Call the existing DB function to update the status
    success = update_reservation_status(reservation_id, new_status)
    
    if not success:
        # This might happen if the reservation_id was valid but something went wrong during update
        raise Exception("Failed to update reservation status in the database.")

    return {"reservation_id": reservation_id, "new_status": new_status}

######################################

def list_payments_by_status_service(status):
    """Service to list payments filtered by their status."""
    if not status:
        raise ValueError("Status parameter is required.")
    
    payments = get_payments_by_status(status)
    return payments


def get_reservation_details_for_admin_service(reservation_id):
    """Service to get full details of a reservation."""
    details = get_full_reservation_details(reservation_id)
    if not details:
        raise ValueError("Reservation not found.")
    return details