from db.db import create_reservation, get_reservations

import logging

def reserve_ticket_service(passenger_id, ticket_id, validity_minutes=10):
    logging.debug(f"reserve_ticket_service called with passenger_id={passenger_id}, ticket_id={ticket_id}, validity_minutes={validity_minutes}")
    reservation_id = create_reservation(passenger_id, ticket_id, validity_minutes)
    logging.debug(f"Reservation created with ID: {reservation_id}")
    return reservation_id


def get_active_reservations_service(passenger_id):
    return get_reservations(passenger_id, active_only=True)

def get_reservation_history_service(passenger_id):
    return get_reservations(passenger_id, active_only=False)
