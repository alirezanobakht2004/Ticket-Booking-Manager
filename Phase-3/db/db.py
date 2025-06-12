import pymysql
from config import Config
import logging

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
            cursor.execute(sql, (passenger_id, now, 'active', expiry_time, now, now))
            reservation_id = cursor.lastrowid

            # Optionally link reservation to ticket by updating ticket or creating a mapping table
            # For now, assume ticket_id is stored elsewhere or handled separately

            return reservation_id
    finally:
        conn.close()

def get_reservations(passenger_id, active_only=True):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if active_only:
                sql = """
                SELECT * FROM reservation
                WHERE passenger_id = %s AND status = 'active' AND expiry_time > NOW()
                ORDER BY reservation_date DESC
                """
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
