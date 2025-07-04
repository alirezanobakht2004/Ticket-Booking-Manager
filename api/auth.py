from flask import Blueprint, request, jsonify, current_app
from services.auth_service import request_otp_service, verify_otp_service, signup_service
from flask import Blueprint, request, jsonify, current_app
from services.auth_service import update_user_profile_service
from utils.jwt_utils import verify_jwt_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    phone = data.get('phone')
    email = data.get('email')
    user_key = phone or email

    current_app.logger.debug(f"Received request for OTP: phone={phone}, email={email}")

    if not user_key:
        current_app.logger.warning("User key (phone or email) is missing.")
        return jsonify({'status': 'error', 'message': 'Phone or email is required.'}), 400

    otp = request_otp_service(user_key, email=email) 

    current_app.logger.debug(f"Generated OTP for user {user_key}: {otp}")

    return jsonify({'status': 'success', 'message': 'OTP sent.', 'otp': otp})


@auth_bp.route('/login/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    email = data.get('email')
    user_key = phone or email
    otp_input = data.get('otp')

    # Log the incoming request
    current_app.logger.debug(f"Received OTP verification request: user_key={user_key}, otp_input={otp_input}")

    if not user_key or not otp_input:
        current_app.logger.warning("Missing user key or OTP input.")
        return jsonify({'status': 'error', 'message': 'User key and OTP required.'}), 400

    ok, result = verify_otp_service(user_key, otp_input, phone=phone, email=email)

    if not ok:
        current_app.logger.error(f"Failed OTP verification: {result}")
        return jsonify({'status': 'error', 'message': result}), 401

    current_app.logger.info(f"Successful OTP verification for user {user_key}")
    return jsonify({'status': 'success', 'token': result})


@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    phone_number = data.get('phone_number')
    city = data.get('city')
    password = data.get('password')

    # Log the signup attempt
    current_app.logger.debug(f"Signup attempt: {email}, {phone_number}")

    # Check for missing fields
    if not all([first_name, last_name, email, phone_number, city, password]):
        current_app.logger.warning("Signup failed: missing fields")
        return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

    # Call the signup service
    success, result = signup_service(first_name, last_name, email, phone_number, city, password)
    
    # If signup fails (e.g., user already exists), return error
    if not success:
        current_app.logger.warning(f"Signup failed: {result}")
        return jsonify({'status': 'error', 'message': result}), 409

    # If signup is successful, return success and JWT token
    current_app.logger.info(f"User created: {email}")
    return jsonify({'status': 'success', 'message': 'User created.', 'token': result}), 201





@auth_bp.route('/profile/update', methods=['POST'])
def update_profile():
    data = request.get_json()
    current_app.logger.debug(f"Update profile data received: {data}")
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Authorization token is required.'}), 400

    # Verify the JWT token
    user_data = verify_jwt_token(token)
    if not user_data:
        return jsonify({'status': 'error', 'message': 'Invalid or expired token.'}), 401

    # Extract user profile details from request
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone_number = data.get('phone_number')
    email = data.get('email')
    city = data.get('city')

    # Check for missing fields
    if not any([first_name, last_name, phone_number, email, city]):
        return jsonify({'status': 'error', 'message': 'At least one field must be provided for update.'}), 400

    # Update the user profile
    success, result = update_user_profile_service(
        user_data['user_id'],
        first_name, last_name, phone_number, email, city
    )
    
    if not success:
        return jsonify({'status': 'error', 'message': result}), 400

    return jsonify({'status': 'success', 'message': 'Profile updated successfully.'}), 200



