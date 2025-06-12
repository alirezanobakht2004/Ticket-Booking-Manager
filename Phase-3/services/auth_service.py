from utils.otp_utils import generate_otp
from services.cache_service import store_otp, get_otp, delete_otp
from utils.jwt_utils import create_jwt
from db.db import find_user_by_phone_or_email
from db.db import user_exists, create_user, create_passenger
from utils.password_utils import hash_password
from utils.jwt_utils import create_jwt
from db.db import update_user_profile, find_user_by_id
from services.cache_service import update_user_cache
from utils.password_utils import check_password

def request_otp_service(user_key):
    otp = generate_otp()
    store_otp(user_key, otp)
    return otp

def verify_otp_service(user_key, otp_input, phone=None, email=None):
    otp_stored = get_otp(user_key)
    if otp_stored is None:
        return False, "OTP expired or not found"
    if otp_input != otp_stored:
        return False, "OTP incorrect"
    delete_otp(user_key)

    # Check user existence in DB
    user = find_user_by_phone_or_email(phone=phone, email=email)
    if not user:
        return False, "User not found"

    jwt_token = create_jwt({'user_id': user['person_id'], 'email': user.get('email'), 'phone': user.get('phone_number')})
    return True, jwt_token

def signup_service(first_name, last_name, email, phone_number, city, password):
    # Check if user exists
    if user_exists(email, phone_number):
        return False, "User with this email or phone already exists."
    
    # Hash password using bcrypt (make sure to install bcrypt)
    password_hashed = hash_password(password)
    
    # Insert into person table
    person_id = create_user(first_name, last_name, email, phone_number, city, password_hashed)
    
    # Insert into passenger table
    create_passenger(person_id)
    
    # Create JWT token
    token = create_jwt({
        'user_id': person_id,
        'email': email,
        'phone': phone_number
    })
    
    return True, token



def update_user_profile_service(user_id, first_name, last_name, phone_number, email, city):
    # Check if user exists
    user = find_user_by_id(user_id)
    if not user:
        return False, "User not found"

    # Update user profile in the database
    success, result = update_user_profile(user_id, first_name, last_name, phone_number, email, city)
    if not success:
        return False, result

    # Update user profile in Redis (cache invalidation and update)
    update_user_cache(user_id, first_name, last_name, phone_number, email, city)

    return True, "Profile updated successfully."
