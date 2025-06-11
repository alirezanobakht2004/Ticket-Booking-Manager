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

def find_user_by_phone_or_email(phone=None, email=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if phone:
                sql = "SELECT * FROM person WHERE phone_number = %s"
                cursor.execute(sql, (phone,))
            elif email:
                sql = "SELECT * FROM person WHERE email = %s"
                cursor.execute(sql, (email,))
            else:
                return None
            return cursor.fetchone()
    finally:
        conn.close()
