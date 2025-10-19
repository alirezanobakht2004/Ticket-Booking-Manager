import pymysql
import logging
from datetime import datetime, timedelta
from config import Config
from typing import Optional, List, Dict, Any


# ---------------------------
# Connection Factory
# ---------------------------
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


# ---------------------------
# User Management Functions
# ---------------------------
def user_exists(email: str, phone_number: str) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT person_id FROM person WHERE email=%s OR phone_number=%s",
                (email, phone_number)
            )
            return cursor.fetchone() is not None
    finally:
        conn.close()


def create_user(first_name: str, last_name: str, email: str, phone_number: str, 
                city: str, password_hashed: str) -> int:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO person (first_name, last_name, email, phone_number, city, password_hashed)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (first_name, last_name, email, phone_number, city, password_hashed))
            return cursor.lastrowid
    finally:
        conn.close()


def create_passenger(person_id: int) -> None:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO passenger (person_id, registered_trips, loyalty_point, passenger_type)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (person_id, None, 0, "NORMAL"))
    finally:
        conn.close()


def find_user_by_phone_or_email(phone: Optional[str] = None, 
                               email: Optional[str] = None) -> Optional[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if phone:
                cursor.execute("SELECT * FROM person WHERE phone_number = %s", (phone,))
            elif email:
                cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
            else:
                return None
            return cursor.fetchone()
    finally:
        conn.close()


def find_user_by_id(user_id: int) -> Optional[Dict]:
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


def find_user_by_email(email: str) -> Optional[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM person WHERE email = %s"
            cursor.execute(sql, (email,))
            return cursor.fetchone()
    finally:
        conn.close()


def update_user_profile(user_id: int, first_name: str, last_name: str, 
                       phone_number: str, email: str, city: str) -> tuple:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE person
                SET first_name=%s, last_name=%s, phone_number=%s, email=%s, city=%s
                WHERE person_id=%s
            """
            cursor.execute(sql, (first_name, last_name, phone_number, email, city, user_id))
            if cursor.rowcount == 0:
                cursor.execute("SELECT 1 FROM person WHERE person_id=%s", (user_id,))
                if cursor.fetchone() is None:
                    return False, "User not found"
            return True, "User profile updated"
    finally:
        conn.close()


# ---------------------------
# City Management Functions
# ---------------------------
def get_all_cities() -> List[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT location_id, title FROM location ORDER BY title ASC")
            return cursor.fetchall()
    finally:
        conn.close()


# ---------------------------
# Ticket Management Functions
# ---------------------------
def search_tickets(origin_id: int, destination_id: int, travel_date: str,
                   vehicle_type: Optional[str] = None, min_price: Optional[float] = None, 
                   max_price: Optional[float] = None, departure_start: Optional[str] = None, 
                   departure_end: Optional[str] = None, travel_class: Optional[str] = None, 
                   company_name: Optional[str] = None) -> List[Dict]:
    """
    SQL-based ticket search with filters.
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

            # Date
            sql += " AND DATE(t.departure_time) = %s "
            params.append(travel_date)

            # Vehicle type
            if vehicle_type == 'plane':
                sql += " AND p.vehicle_id IS NOT NULL "
            elif vehicle_type == 'bus':
                sql += " AND b.vehicle_id IS NOT NULL "
            elif vehicle_type == 'train':
                sql += " AND tr.vehicle_id IS NOT NULL "

            # Price
            if min_price is not None:
                sql += " AND t.price >= %s "
                params.append(min_price)
            if max_price is not None:
                sql += " AND t.price <= %s "
                params.append(max_price)

            # Time window
            if departure_start is not None:
                sql += " AND TIME(t.departure_time) >= %s "
                params.append(departure_start)
            if departure_end is not None:
                sql += " AND TIME(t.departure_time) <= %s "
                params.append(departure_end)

            # Class
            if travel_class is not None:
                sql += " AND t.class_code = %s "
                params.append(travel_class)

            # Company name in any carrier column
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


def get_ticket_details(ticket_id: int) -> Optional[Dict]:
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


def get_ticket_for_cancellation_check(ticket_id: int) -> Optional[Dict]:
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


def get_ticket_owner_person_id(ticket_id: int) -> Optional[int]:
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


# ---------------------------
# Reservation Management Functions
# ---------------------------
def create_reservation(passenger_id: int, ticket_id: int, validity_minutes: int = 10) -> int:
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
            cursor.execute(sql, (passenger_id, now, 'PENDING', expiry_time, now, now))
            reservation_id = cursor.lastrowid
            logging.debug(f"Inserted reservation with ID: {reservation_id}")

            # Link ticket to reservation for payment aggregation
            cursor.execute(
                "UPDATE ticket SET reservation_id = %s WHERE ticket_id = %s",
                (reservation_id, ticket_id)
            )

            return reservation_id
    except Exception as e:
        logging.error(f"Error creating reservation: {e}")
        raise
    finally:
        conn.close()


def get_reservations(passenger_id: int, active_only: bool = True) -> List[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if active_only:
                now = datetime.utcnow()
                # Accept both legacy 'active' and new 'PENDING' as active-like, and ensure not expired
                sql = """
                    SELECT *
                    FROM reservation
                    WHERE passenger_id = %s
                      AND status IN ('PENDING', 'active')
                      AND expiry_time > %s
                    ORDER BY reservation_date DESC
                """
                cursor.execute(sql, (passenger_id, now))
            else:
                sql = """
                    SELECT *
                    FROM reservation
                    WHERE passenger_id = %s
                    ORDER BY reservation_date DESC
                """
                cursor.execute(sql, (passenger_id,))
            return cursor.fetchall()
    finally:
        conn.close()


def get_reservation_by_id(reservation_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM reservation WHERE reservation_id = %s", (reservation_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_reservation_by_ticket_id(ticket_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
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


def find_reservation_by_ticket_id(ticket_id: int) -> Optional[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
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


def update_reservation_status(reservation_id: int, new_status: str) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE reservation SET status = %s, updated_at = %s WHERE reservation_id = %s"
            cursor.execute(sql, (new_status, datetime.utcnow(), reservation_id))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ---------------------------
# Payment Management Functions
# ---------------------------
def get_total_amount_for_reservation(reservation_id: int) -> float:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT SUM(price) AS total_amount FROM ticket WHERE reservation_id = %s"
            cursor.execute(sql, (reservation_id,))
            result = cursor.fetchone()
            return (result['total_amount'] or 0) if result is not None else 0
    finally:
        conn.close()


def create_payment_record(reservation_id: int, amount: float, method: str, 
                         status: str, transaction_ref: str) -> int:
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


def get_finalized_ticket_details(reservation_id: int) -> List[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT ticket_id, vehicle_id, price, departure_time, arrival_time
                FROM ticket
                WHERE reservation_id = %s
            """
            cursor.execute(sql, (reservation_id,))
            return cursor.fetchall()
    finally:
        conn.close()


# ---------------------------
# Wallet Management Functions
# ---------------------------
def add_to_user_wallet(person_id: int, amount_to_add: float) -> bool:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE person
                SET wallet_balance = wallet_balance + %s
                WHERE person_id = %s
            """
            cursor.execute(sql, (amount_to_add, person_id))
            return cursor.rowcount > 0
    finally:
        conn.close()


# ---------------------------
# Report Management Functions
# ---------------------------
def get_all_reports() -> List[Dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
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


def get_reservations_by_status(status: str) -> List[Dict]:
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


# ---------------------------
# ElasticSearch Integration Functions
# ---------------------------
def get_all_tickets_for_indexing() -> List[Dict]:
    """
    Returns a flattened list of tickets suitable for ES indexing.
    Adjust selected columns to match your ES document schema.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    t.ticket_id,
                    t.vehicle_id,
                    t.reservation_id,
                    t.source AS origin_id,
                    t.destination AS destination_id,
                    src.title AS origin_city,
                    dst.title AS destination_city,
                    t.departure_time,
                    t.arrival_time,
                    t.price,
                    t.class_code,
                    v.brand,
                    v.model,
                    -- Derive vehicle_type by joins:
                    CASE
                        WHEN b.vehicle_id IS NOT NULL THEN 'bus'
                        WHEN p.vehicle_id IS NOT NULL THEN 'plane'
                        WHEN tr.vehicle_id IS NOT NULL THEN 'train'
                        ELSE NULL
                    END AS vehicle_type,
                    COALESCE(b.bus_company, p.airline_name, tr.train_type) AS company_name,
                    v.capacity,
                    v.reserved_number
                FROM ticket t
                JOIN location src ON t.source = src.location_id
                JOIN location dst ON t.destination = dst.location_id
                JOIN vehicle v ON t.vehicle_id = v.vehicle_id
                LEFT JOIN bus b ON v.vehicle_id = b.vehicle_id
                LEFT JOIN plane p ON v.vehicle_id = p.vehicle_id
                LEFT JOIN train tr ON v.vehicle_id = tr.vehicle_id
            """
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        conn.close()


def get_flat_ticket_by_id(ticket_id: int) -> Optional[Dict]:
    """
    Returns one flattened ticket suitable for ES indexing.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    t.ticket_id,
                    t.vehicle_id,
                    t.reservation_id,
                    t.source AS origin_id,
                    t.destination AS destination_id,
                    src.title AS origin_city,
                    dst.title AS destination_city,
                    t.departure_time,
                    t.arrival_time,
                    t.price,
                    t.class_code,
                    v.brand,
                    v.model,
                    CASE
                        WHEN b.vehicle_id IS NOT NULL THEN 'bus'
                        WHEN p.vehicle_id IS NOT NULL THEN 'plane'
                        WHEN tr.vehicle_id IS NOT NULL THEN 'train'
                        ELSE NULL
                    END AS vehicle_type,
                    COALESCE(b.bus_company, p.airline_name, tr.train_type) AS company_name,
                    v.capacity,
                    v.reserved_number
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
        
def get_full_reservation_details(reservation_id: int):
    """
    Fetch a reservation with requester details and all its tickets (flattened).
    Adjust field names to your schema as needed.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            reservation_sql = """
                SELECT
                    r.reservation_id,
                    r.passenger_id,
                    r.status,
                    r.reservation_date,
                    r.expiry_time,
                    r.created_at,
                    r.updated_at,
                    p.person_id,
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
            reservation = cursor.fetchone()
            if not reservation:
                return None

            tickets_sql = """
                SELECT
                    t.ticket_id,
                    t.price,
                    t.departure_time,
                    t.arrival_time,
                    src.title AS origin_city,
                    dst.title AS destination_city
                FROM ticket t
                JOIN location src ON t.source = src.location_id
                JOIN location dst ON t.destination = dst.location_id
                WHERE t.reservation_id = %s
                ORDER BY t.departure_time ASC
            """
            cursor.execute(tickets_sql, (reservation_id,))
            tickets = cursor.fetchall() or []

            reservation["tickets"] = tickets
            return reservation
    finally:
        conn.close()
        
def get_payments_by_status(status: str) -> list[dict]:
    """
    Return payments filtered by status (e.g., 'FAILED', 'SUCCESSFUL', 'PENDING'),
    with basic reservation and user context for admin views.
    Adjust field names if your schema differs.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    pay.payment_id,
                    pay.reservation_id,
                    pay.amount,
                    pay.payment_method,
                    pay.status,
                    pay.transaction_reference,
                    pay.created_at,
                    r.passenger_id,
                    r.status AS reservation_status,
                    p.person_id,
                    p.first_name,
                    p.last_name,
                    p.email,
                    p.phone_number
                FROM payment pay
                LEFT JOIN reservation r ON pay.reservation_id = r.reservation_id
                LEFT JOIN passenger ps ON r.passenger_id = ps.person_id
                LEFT JOIN person p ON ps.person_id = p.person_id
                WHERE pay.status = %s
                ORDER BY pay.created_at DESC
            """
            cursor.execute(sql, (status,))
            return cursor.fetchall()
    finally:
        conn.close()
        
def get_passenger_id_from_person_id(person_id: int) -> Optional[int]:
    """
    Returns the passenger_id (same as person_id in your schema) if a passenger row exists.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT person_id FROM passenger WHERE person_id = %s"
            cursor.execute(sql, (person_id,))
            row = cursor.fetchone()
            return row["person_id"] if row else None
    finally:
        conn.close()
        
def get_user_tickets_by_filter(
    person_id: int,
    status: Optional[str] = None,
    start_date: Optional[str] = None,  # 'YYYY-MM-DD'
    end_date: Optional[str] = None,    # 'YYYY-MM-DD'
    vehicle_type: Optional[str] = None # 'plane'|'bus'|'train'
) -> list[dict]:
    """
    Returns tickets for a given user (by person_id), with optional filters:
      - reservation status (e.g., 'PENDING','CONFIRMED','CANCELLED')
      - date range on ticket.departure_time (YYYY-MM-DD strings)
      - vehicle_type filter via joins
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    t.ticket_id,
                    t.price,
                    t.departure_time,
                    t.arrival_time,
                    src.title AS origin_city,
                    dst.title AS destination_city,
                    r.reservation_id,
                    r.status AS reservation_status,
                    CASE
                        WHEN b.vehicle_id IS NOT NULL THEN 'bus'
                        WHEN p.vehicle_id IS NOT NULL THEN 'plane'
                        WHEN tr.vehicle_id IS NOT NULL THEN 'train'
                        ELSE 'unknown'
                    END AS vehicle_type
                FROM ticket t
                JOIN reservation r ON t.reservation_id = r.reservation_id
                JOIN passenger ps ON r.passenger_id = ps.person_id
                JOIN person pe ON ps.person_id = pe.person_id
                JOIN location src ON t.source = src.location_id
                JOIN location dst ON t.destination = dst.location_id
                JOIN vehicle v ON t.vehicle_id = v.vehicle_id
                LEFT JOIN bus b ON v.vehicle_id = b.vehicle_id
                LEFT JOIN plane p ON v.vehicle_id = p.vehicle_id
                LEFT JOIN train tr ON v.vehicle_id = tr.vehicle_id
                WHERE pe.person_id = %s
            """
            params: list[Any] = [person_id]

            if status:
                sql += " AND r.status = %s "
                params.append(status)

            if start_date:
                sql += " AND DATE(t.departure_time) >= %s "
                params.append(start_date)

            if end_date:
                sql += " AND DATE(t.departure_time) <= %s "
                params.append(end_date)

            if vehicle_type:
                if vehicle_type == "plane":
                    sql += " AND p.vehicle_id IS NOT NULL "
                elif vehicle_type == "bus":
                    sql += " AND b.vehicle_id IS NOT NULL "
                elif vehicle_type == "train":
                    sql += " AND tr.vehicle_id IS NOT NULL "

            sql += " ORDER BY t.departure_time DESC "

            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        conn.close()
        
def create_report(
    person_id: int,
    ticket_id: int,
    report_type: str,
    report_text: str,
    status: str = "OPEN"
) -> int:
    """
    Inserts a new report into the 'report' table and returns the created report_id.
    Columns used (adjust if your schema differs):
      - person_id: who reports
      - ticket_id: the ticket being reported (nullable if your schema allows)
      - report_type: e.g., 'BUG', 'PAYMENT', 'CANCEL', 'OTHER'
      - report_text: free text
      - status: e.g., 'OPEN', 'IN_REVIEW', 'RESOLVED', 'REJECTED'
      - created_at: default NOW() at DB level or set explicitly here
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO report (person_id, ticket_id, report_type, report_text, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            now = datetime.utcnow()
            cursor.execute(sql, (person_id, ticket_id, report_type, report_text, status, now))
            conn.commit()
            return cursor.lastrowid
    finally:
        conn.close()