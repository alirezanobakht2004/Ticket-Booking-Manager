from flask import Blueprint, request, jsonify
from services.auth_service import request_otp_service, verify_otp_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/request-otp', methods=['POST'])
def request_otp():
    data = request.get_json()
    phone = data.get('phone')
    email = data.get('email')
    user_key = phone or email
    if not user_key:
        return jsonify({'status': 'error', 'message': 'Phone or email is required.'}), 400
    otp = request_otp_service(user_key)
    return jsonify({'status': 'success', 'message': 'OTP sent.', 'otp': otp})

@auth_bp.route('/login/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    phone = data.get('phone')
    email = data.get('email')
    user_key = phone or email
    otp_input = data.get('otp')
    if not user_key or not otp_input:
        return jsonify({'status': 'error', 'message': 'User key and OTP required.'}), 400
    ok, result = verify_otp_service(user_key, otp_input, phone=phone, email=email)
    if not ok:
        return jsonify({'status': 'error', 'message': result}), 401
    return jsonify({'status': 'success', 'token': result})


@auth_bp.route('/signup', methods=['POST'])
def signup():
    # Parse user data, hash password, save to DB, return JWT
    return jsonify({'status': 'success', 'message': 'User created.'})
