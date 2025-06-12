import pymysql
from config import Config

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
            if cursor.rowcount == 0:
                return False, "User not found"
            return True, "User profile updated"
    finally:
        conn.close()
        
        
        
def find_user_by_id(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM person WHERE person_id = %s", (user_id,))
            return cursor.fetchone()  # This returns the user data or None if not found
    finally:
        conn.close()