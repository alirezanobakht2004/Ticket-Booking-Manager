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

def find_reservation_by_ticket_id(ticket_id):
    """Finds reservation details associated with a given ticket_id."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Join ticket and reservation tables to get reservation info from a ticket
            sql = """
            SELECT r.*
            FROM reservation r
            JOIN ticket t ON r.reservation_id = t.reservation_id
            WHERE t.ticket_id = %s
            """
            cursor.execute(sql, (ticket_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_total_amount_for_reservation(reservation_id):
    """Calculates the sum of all ticket prices for a reservation."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT SUM(price) as total_amount FROM ticket WHERE reservation_id = %s"
            cursor.execute(sql, (reservation_id,))
            result = cursor.fetchone()
            return result['total_amount'] if result else 0
    finally:
        conn.close()

def create_payment_record(reservation_id, amount, method, status, transaction_ref):
    """Creates a new record in the payment table."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO payment (reservation_id, amount, payment_method, status, transaction_reference)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (reservation_id, amount, method, status, transaction_ref))
            return cursor.lastrowid
    finally:
        conn.close()

def update_reservation_status(reservation_id, new_status):
    """Updates the status of a specific reservation."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # We also update `updated_at` manually for clarity, though the DB might do it.
            sql = "UPDATE reservation SET status = %s, updated_at = %s WHERE reservation_id = %s"
            cursor.execute(sql, (new_status, datetime.now(), reservation_id))
            return cursor.rowcount > 0 # Returns True if a row was updated
    finally:
        conn.close()

def get_finalized_ticket_details(reservation_id):
    """Retrieves all ticket details for a confirmed reservation."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT ticket_id, vehicle_id, price, departure_time, arrival_time FROM ticket WHERE reservation_id = %s"
            cursor.execute(sql, (reservation_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def get_ticket_for_cancellation_check(ticket_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT
                t.ticket_id,
                t.price,
                t.departure_time,
                r.status AS reservation_status,
                CASE
                    WHEN b.vehicle_id IS NOT NULL THEN 'bus'
                    WHEN p.vehicle_id IS NOT NULL THEN 'plane'
                    WHEN tr.vehicle_id IS NOT NULL THEN 'train'
                    ELSE 'unknown'
                END AS vehicle_type
            FROM ticket t
            JOIN reservation r ON t.reservation_id = r.reservation_id
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

###############################

def get_reservations_by_status(status):
    """Fetches all reservations with a specific status, including passenger info."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT
                r.reservation_id,
                r.status,
                r.reservation_date,
                r.expiry_time,
                p.person_id,
                p.first_name,
                p.last_name
            FROM reservation r
            JOIN passenger ps ON r.passenger_id = ps.person_id
            JOIN person p ON ps.person_id = p.person_id
            WHERE r.status = %s
            ORDER BY r.updated_at DESC
            """
            cursor.execute(sql, (status,))
            return cursor.fetchall()
    finally:
        conn.close()


# --- FIX IS IN THIS FUNCTION ---
def get_all_reports():
    """
    Fetches all user reports from the database using the correct column names.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # This query has been updated to match your 'report' table schema.
            sql = """
            SELECT
                rep.report_id,
                rep.report_type,
                rep.report_text,
                rep.status AS report_status,
                rep.created_at,
                rep.ticket_id,
                p.person_id AS reporter_id,
                p.first_name,
                p.last_name
            FROM report rep
            JOIN person p ON rep.person_id = p.person_id
            ORDER BY rep.created_at DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()

def get_reservation_by_id(reservation_id):
    """Fetches a single reservation by its ID."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reservation WHERE reservation_id = %s", (reservation_id,))
            return cursor.fetchone()
    finally:
        conn.close()

############################################
def get_passenger_id_from_person_id(person_id):
    """
    Finds the passenger record for a given person_id and returns the person_id
    to be used as the identifier in the reservation table.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # FIX: Select the 'person_id' column, not 'passenger_id'.
            # This query confirms a passenger record exists for the person.
            sql = "SELECT person_id FROM passenger WHERE person_id = %s"
            cursor.execute(sql, (person_id,))
            result = cursor.fetchone()
            
            # If a result is found, return the person_id. This is what's used in the reservation table.
            return result['person_id'] if result else None
    finally:
        conn.close()



def get_user_tickets_by_filter(passenger_id, filter_type):
    """
    Fetches a user's tickets based on a filter.
    Filters: 'upcoming', 'past', 'cancelled'
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Base query joins ticket with reservation and vehicle details
            sql = """
            SELECT
                t.ticket_id,
                t.departure_time,
                t.arrival_time,
                t.price,
                r.status AS reservation_status,
                v.brand,
                orig.title AS origin_city,
                dest.title AS destination_city
            FROM ticket t
            JOIN reservation r ON t.reservation_id = r.reservation_id
            JOIN vehicle v ON t.vehicle_id = v.vehicle_id
            JOIN location orig ON t.source = orig.location_id
            JOIN location dest ON t.destination = dest.location_id
            WHERE r.passenger_id = %s
            """
            
            params = [passenger_id]
            now_utc = datetime.utcnow()

            # Apply filter logic
            if filter_type == 'upcoming':
                sql += " AND r.status = 'CONFIRMED' AND t.departure_time > %s"
                params.append(now_utc)
            elif filter_type == 'past':
                sql += " AND r.status = 'CONFIRMED' AND t.departure_time <= %s"
                params.append(now_utc)
            elif filter_type == 'cancelled':
                sql += " AND r.status = 'CANCELLED'"
            else: # Default to upcoming if filter is invalid or not provided
                sql += " AND r.status = 'CONFIRMED' AND t.departure_time > %s"
                params.append(now_utc)

            sql += " ORDER BY t.departure_time DESC"
            
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()


#############################################33

def get_ticket_owner_person_id(ticket_id):
    """Finds the person_id of the user who owns the reservation for a given ticket."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.person_id
            FROM person p
            JOIN passenger ps ON p.person_id = ps.person_id
            JOIN reservation r ON ps.person_id = r.passenger_id
            JOIN ticket t ON r.reservation_id = t.reservation_id
            WHERE t.ticket_id = %s
            """
            cursor.execute(sql, (ticket_id,))
            result = cursor.fetchone()
            return result['person_id'] if result else None
    finally:
        conn.close()


def add_to_user_wallet(person_id, amount_to_add):
    """
    Adds a specified amount to the user's wallet balance.
    Assumes a 'wallet_balance' column exists in the 'person' table.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # This query safely increments the wallet balance.
            sql = """
            UPDATE person
            SET wallet_balance = wallet_balance + %s
            WHERE person_id = %s
            """
            cursor.execute(sql, (amount_to_add, person_id))
            return cursor.rowcount > 0 # Returns True if a row was updated
    finally:
        conn.close()

##########################################
def get_ticket_owner_person_id(ticket_id):
    """Finds the person_id of the user who owns the reservation for a given ticket."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT p.person_id
            FROM person p
            JOIN passenger ps ON p.person_id = ps.person_id
            JOIN reservation r ON ps.person_id = r.passenger_id
            JOIN ticket t ON r.reservation_id = t.reservation_id
            WHERE t.ticket_id = %s
            """
            cursor.execute(sql, (ticket_id,))
            result = cursor.fetchone()
            return result['person_id'] if result else None
    finally:
        conn.close()


def add_to_user_wallet(person_id, amount_to_add):
    """
    Adds a specified amount to the user's wallet balance.
    Assumes a 'wallet_balance' column exists in the 'person' table.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # This query safely increments the wallet balance.
            sql = """
            UPDATE person
            SET wallet_balance = wallet_balance + %s
            WHERE person_id = %s
            """
            cursor.execute(sql, (amount_to_add, person_id))
            return cursor.rowcount > 0 # Returns True if a row was updated
    finally:
        conn.close()

def get_reservation_by_ticket_id(ticket_id):
    """Finds the entire reservation record associated with a given ticket_id."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Join ticket and reservation tables to get reservation info from a ticket
            sql = """
            SELECT r.*
            FROM reservation r
            JOIN ticket t ON r.reservation_id = t.reservation_id
            WHERE t.ticket_id = %s
            """
            cursor.execute(sql, (ticket_id,))
            return cursor.fetchone()
    finally:
        conn.close()

#########################################33
def create_report(person_id, ticket_id, report_type, report_text):
    """
    Creates a new report in the database submitted by a user.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # We assume the report table has these columns.
            # The status defaults to 'OPEN' or a similar initial state.
            sql = """
            INSERT INTO report (person_id, ticket_id, report_type, report_text, status)
            VALUES (%s, %s, %s, %s, %s)
            """
            # The initial status for a new report is 'OPEN'
            cursor.execute(sql, (person_id, ticket_id, report_type, report_text, 'OPEN'))
            return cursor.lastrowid
    finally:
        conn.close()


##########################################33

def get_payments_by_status(status):
    """Fetches all payments with a specific status, including user and reservation info."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            SELECT
                pay.payment_id,
                pay.payment_method,
                pay.amount,
                pay.status,
                pay.payment_time,
                r.reservation_id,
                p.person_id,
                p.first_name,
                p.last_name
            FROM payment pay
            JOIN reservation r ON pay.reservation_id = r.reservation_id
            JOIN passenger ps ON r.passenger_id = ps.person_id
            JOIN person p ON ps.person_id = p.person_id
            WHERE pay.status = %s
            ORDER BY pay.payment_time DESC
            """
            cursor.execute(sql, (status,))
            return cursor.fetchall()
    finally:
        conn.close()


def get_full_reservation_details(reservation_id):
    """
    Fetches detailed information for a single reservation, including all its tickets.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # First, get reservation and passenger details
            reservation_sql = """
            SELECT
                r.*,
                p.first_name,
                p.last_name,
                p.email,
                p.phone_number
            FROM reservation r
            JOIN passenger ps ON r.passenger_id = ps.person_id
            JOIN person p ON ps.person_id = p.person_id
            WHERE r.reservation_id = %s
            """
            cursor.execute(reservation_sql, (reservation_id,))
            reservation_details = cursor.fetchone()

            if not reservation_details:
                return None

            # Second, get all tickets associated with this reservation
            tickets_sql = """
            SELECT
                t.ticket_id,
                t.price,
                t.departure_time,
                t.arrival_time,
                orig.title as origin_city,
                dest.title as destination_city
            FROM ticket t
            JOIN location orig ON t.source = orig.location_id
            JOIN location dest ON t.destination = dest.location_id
            WHERE t.reservation_id = %s
            """
            cursor.execute(tickets_sql, (reservation_id,))
            tickets = cursor.fetchall()
            
            reservation_details['tickets'] = tickets
            return reservation_details
    finally:
        conn.close()