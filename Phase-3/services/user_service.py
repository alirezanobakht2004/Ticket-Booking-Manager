from db.db import get_passenger_id_from_person_id, get_user_tickets_by_filter
import logging

def get_user_bookings_service(person_id: int, filter_type: str):
    """
    Service to get a user's bookings (tickets) based on a filter.
    """
    # First, get the passenger_id from the person_id
    passenger_id = get_passenger_id_from_person_id(person_id)
    
    if not passenger_id:
        # This case should ideally not happen for a logged-in user
        raise ValueError("No matching passenger profile found for this user.")
        
    # Fetch the tickets from the database using the passenger_id and filter
    tickets = get_user_tickets_by_filter(passenger_id, filter_type)
    
    return tickets
