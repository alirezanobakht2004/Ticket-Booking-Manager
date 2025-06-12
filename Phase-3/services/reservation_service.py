from db.db import create_reservation, get_reservations

def reserve_ticket_service(passenger_id, ticket_id, validity_minutes=10):
    # Here you can add logic to check ticket availability, etc.
    reservation_id = create_reservation(passenger_id, ticket_id, validity_minutes)
    return reservation_id

def get_active_reservations_service(passenger_id):
    return get_reservations(passenger_id, active_only=True)

def get_reservation_history_service(passenger_id):
    return get_reservations(passenger_id, active_only=False)
