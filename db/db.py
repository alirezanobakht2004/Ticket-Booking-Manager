import pymysql
from config import Config
import logging
from flask import g
from datetime import datetime
import uuid

def get_db_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )
    
def user_exists(email, phone_number):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT person_id FROM person WHERE email=%s OR phone_number=%s", (email, phone_number))
            return cursor.fetchone() is not None
    finally:
        conn.close()

def create_user(first_name, last_name, email, phone_number, city, password_hashed):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO person (first_name, last_name, email, phone_number, city, password_hashed)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (first_name, last_name, email, phone_number, city, password_hashed))
            return cursor.lastrowid  # Return the person_id of the newly created user
    finally:
        conn.close()

def create_passenger(person_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO passenger (person_id, registered_trips, loyalty_point, passenger_type)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (person_id, None, 0, "NORMAL"))  # Default loyalty point and passenger type
    finally:
        conn.close()

def find_user_by_phone_or_email(phone=None, email=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if phone:
                cursor.execute("SELECT * FROM person WHERE phone_number = %s", (phone,))
            elif email:
                cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
            else:
                return None
            return cursor.fetchone()  # This returns the user row, or None if not found
    finally:
        conn.close()



def update_user_profile(user_id, first_name, last_name, phone_number, email, city):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE person 
            SET first_name=%s, last_name=%s, phone_number=%s, email=%s, city=%s
            WHERE person_id=%s
            """
            cursor.execute(sql, (first_name, last_name, phone_number, email, city, user_id))
            # If no rows affected, check if user exists
            if cursor.rowcount == 0:
                # Double-check user existence to distinguish no change vs no user
                cursor.execute("SELECT 1 FROM person WHERE person_id=%s", (user_id,))
                if cursor.fetchone() is None:
                    return False, "User not found"
            return True, "User profile updated"
    finally:
        conn.close()

def find_user_by_id(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM person WHERE person_id = %s", (user_id,))
            user = cursor.fetchone()
            if user:
                logging.debug(f"User found in DB: {user}")
            else:
                logging.debug(f"No user found with person_id={user_id}")
            return user
    finally:
        conn.close()

def get_all_cities():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT location_id, title FROM location ORDER BY title ASC")
            return cursor.fetchall()  # Returns list of dicts with keys: location_id, title
    finally:
        conn.close()

def search_tickets(origin_id, destination_id, travel_date, vehicle_type=None,
                   min_price=None, max_price=None,
                   departure_start=None, departure_end=None,
                   travel_class=None, company_name=None):
    """
    Search tickets with filters.
    - travel_date: date string 'YYYY-MM-DD'
    - vehicle_type: 'plane', 'train', 'bus' or None (all)
    - min_price, max_price: float or None
    - departure_start, departure_end: 'HH:MM' or None
    - travel_class: int or None
    - company_name: string or None (filter by bus_company, airline_name, or train_type)
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT t.ticket_id, t.source, t.destination, t.departure_time, t.arrival_time,
                   t.price, t.class_code, v.brand, v.model,
                   b.bus_company, p.airline_name, tr.train_type
            FROM ticket t
            JOIN vehicle v ON t.vehicle_id = v.vehicle_id
            LEFT JOIN bus b ON v.vehicle_id = b.vehicle_id
            LEFT JOIN plane p ON v.vehicle_id = p.vehicle_id
            LEFT JOIN train tr ON v.vehicle_id = tr.vehicle_id
            """

            sql += " WHERE t.source = %s AND t.destination = %s "
            params = [origin_id, destination_id]

            # Filter by travel_date (date part of departure_time)
            sql += " AND DATE(t.departure_time) = %s "
            params.append(travel_date)

            # Filter by vehicle_type
            if vehicle_type == 'plane':
                sql += " AND p.vehicle_id IS NOT NULL "
            elif vehicle_type == 'bus':
                sql += " AND b.vehicle_id IS NOT NULL "
            elif vehicle_type == 'train':
                sql += " AND tr.vehicle_id IS NOT NULL "

            # Price filter
            if min_price is not None:
                sql += " AND t.price >= %s "
                params.append(min_price)
            if max_price is not None:
                sql += " AND t.price <= %s "
                params.append(max_price)

            # Departure time range filter (time part of departure_time)
            if departure_start is not None:
                sql += " AND TIME(t.departure_time) >= %s "
                params.append(departure_start)
            if departure_end is not None:
                sql += " AND TIME(t.departure_time) <= %s "
                params.append(departure_end)

            # Travel class filter
            if travel_class is not None:
                sql += " AND t.class_code = %s "
                params.append(travel_class)

            # Company name filter (search in bus_company, airline_name, train_type)
            if company_name:
                sql += """
                AND (
                    b.bus_company LIKE %s OR
                    p.airline_name LIKE %s OR
                    tr.train_type LIKE %s
                )
                """
                like_pattern = f"%{company_name}%"
                params.extend([like_pattern, like_pattern, like_pattern])

            sql += " ORDER BY t.departure_time ASC "

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


def get_ticket_details(ticket_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT
                t.ticket_id,
                t.departure_time,
                t.arrival_time,
                t.price,
                t.class_code,
                src.title AS origin,
                dst.title AS destination,
                v.capacity,
                v.reserved_number,
                b.bus_type, b.bus_company, b.chair_decoration, b.air_condition, b.internet_connection, b.snack_service,
                p.airline_name, p.plane_type, p.stops_number, p.flight_number, p.destination_airport, p.departure_airport,
                p.internet_connection AS plane_internet_connection, p.closed_compartment, p.bed_chair,
                tr.train_type, tr.wagon_count, tr.star, tr.bus_train, tr.food_service, tr.internet_connection AS train_internet_connection,
                tr.closed_compartment AS train_closed_compartment
            FROM ticket t
            JOIN location src ON t.source = src.location_id
            JOIN location dst ON t.destination = dst.location_id
            JOIN vehicle v ON t.vehicle_id = v.vehicle_id
            LEFT JOIN bus b ON v.vehicle_id = b.vehicle_id
            LEFT JOIN plane p ON v.vehicle_id = p.vehicle_id
            LEFT JOIN train tr ON v.vehicle_id = tr.vehicle_id
            WHERE t.ticket_id = %s
            """
            cursor.execute(sql, (ticket_id,))
            return cursor.fetchone()
    finally:
        conn.close()

from datetime import datetime, timedelta

import logging
from datetime import datetime, timedelta

def create_reservation(passenger_id, ticket_id, validity_minutes=10):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            expiry_time = datetime.utcnow() + timedelta(minutes=validity_minutes)
            sql = """
            INSERT INTO reservation (passenger_id, reservation_date, status, expiry_time, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            now = datetime.utcnow()
            logging.debug(f"Executing SQL: {sql} with passenger_id={passenger_id}, expiry_time={expiry_time}")
            cursor.execute(sql, (passenger_id, now, 'active', expiry_time, now, now))
            reservation_id = cursor.lastrowid
            logging.debug(f"Inserted reservation with ID: {reservation_id}")

            # TODO: Link reservation to ticket_id if needed

            return reservation_id
    except Exception as e:
        logging.error(f"Error creating reservation: {e}")
        raise
    finally:
        conn.close()


def get_reservations(passenger_id, active_only=True):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if active_only:
                now = datetime.utcnow()
                sql = """
                SELECT * FROM reservation
                WHERE passenger_id = %s AND status = 'active' AND expiry_time > %s
                ORDER BY reservation_date DESC
                """
                cursor.execute(sql, (passenger_id, now))
            else:
                sql = """
                SELECT * FROM reservation
                WHERE passenger_id = %s
                ORDER BY reservation_date DESC
                """
                cursor.execute(sql, (passenger_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def find_user_by_email(email):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM person WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
            return user  # Returns None if not found, or dict-like user record
    finally:
        conn.close()



############ The new functions start here ############

def find_active_reservation_for_ticket_db(ticket_id):

    """
    Finds a PENDING reservation by one of the ticket IDs it contains.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Step 1: Find the reservation_id from the ticket
            cursor.execute("SELECT reservation_id FROM ticket WHERE ticket_id = %s", (ticket_id,))
            ticket_info = cursor.fetchone()

            if not ticket_info or not ticket_info.get('reservation_id'):
                return None

            reservation_id = ticket_info['reservation_id']
            # Step 2: Find the reservation if it's pending and not expired
            sql = """
            SELECT * FROM reservation
            WHERE reservation_id = %s
              AND status = 'PENDING'
            """
            cursor.execute(sql, (reservation_id,))
            return cursor.fetchone()
    except pymysql.Error as e:
        logging.error(f"Database error in find_active_reservation_for_ticket_db: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_tickets_for_reservation_db(reservation_id):
    """
    Retrieves all ticket details for a given reservation ID.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM ticket WHERE reservation_id = %s"
            cursor.execute(sql, (reservation_id,))
            return cursor.fetchall()
    except pymysql.Error as e:
        logging.error(f"Database error in get_tickets_for_reservation_db: {e}")
        raise
    finally:
        if conn:
            conn.close()

def update_reservation_status_db(reservation_id, status):
    """
    Updates the status of a specific reservation (e.g., to 'CONFIRMED' or 'EXPIRED').
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # The `updated_at` column updates automatically based on your schema
            sql = "UPDATE reservation SET status = %s WHERE reservation_id = %s"
            cursor.execute(sql, (status, reservation_id))
            # `autocommit=True` handles the commit
    except Exception as e:
        logging.error(f"Failed to update reservation status for {reservation_id}: {e}")
        raise
    finally:
        if conn:
            conn.close()

def create_payment_db(reservation_id, method, amount, status='PAID'):
    """
    Inserts a new record into the payment table.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            transaction_ref = str(uuid.uuid4()) # Generate a unique reference
            sql = """
            INSERT INTO payment (reservation_id, payment_method, amount, payment_time, status, transaction_reference)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (reservation_id, method, amount, datetime.utcnow(), status, transaction_ref))
            # `autocommit=True` handles the commit
            return cursor.lastrowid
    except Exception as e:
        logging.error(f"Failed to create payment record for reservation {reservation_id}: {e}")
        raise
    finally:
        if conn:
            conn.close()

