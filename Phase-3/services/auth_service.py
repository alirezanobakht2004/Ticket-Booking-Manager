from utils.otp_utils import generate_otp
from services.cache_service import store_otp, get_otp, delete_otp
from utils.jwt_utils import create_jwt

def request_otp_service(user_key):
    otp = generate_otp()
    store_otp(user_key, otp)
    # Here, instead of actually sending SMS/email, just log or return the OTP for dev/demo
    return otp

def verify_otp_service(user_key, otp_input):
    otp_stored = get_otp(user_key)
    if otp_stored is None:
        return False, "OTP expired or not found"
    if otp_input != otp_stored:
        return False, "OTP incorrect"
    delete_otp(user_key)
    # Here, you would look up user in DB and generate a JWT with their info
    # For demo, just make a payload
    jwt_token = create_jwt({'user': user_key})
    return True, jwt_token
