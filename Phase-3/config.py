import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretkey')
    
    # MySQL/MariaDB
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'adminer')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'adminer')
    DB_NAME = os.environ.get('DB_NAME', 'alibaba_db')
    
    # Redis
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    
    # Email
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'your_email@example.com')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'your_email_password')
    SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 465))
    
    # SMS
    SMSIR_API_KEY = os.getenv("SMSIR_API_KEY")  # set in environment
    SMSIR_TEMPLATE_ID = int(os.getenv("SMSIR_TEMPLATE_ID", "245375"))  # sms template
