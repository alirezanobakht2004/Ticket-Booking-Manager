from utils.otp_utils import generate_otp
from services.cache_service import store_otp, get_otp, delete_otp
from utils.jwt_utils import create_jwt
from db.db import find_user_by_phone_or_email

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
