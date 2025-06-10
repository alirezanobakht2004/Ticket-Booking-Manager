from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login/request-otp', methods=['POST'])
def request_otp():
    # Parse phone/email, generate OTP, save in Redis, return success
    return jsonify({'status': 'success', 'message': 'OTP sent.'})

@auth_bp.route('/login/verify-otp', methods=['POST'])
def verify_otp():
    # Parse phone/email, OTP; check Redis, return JWT if valid
    return jsonify({'status': 'success', 'token': 'fake_jwt_token'})

@auth_bp.route('/signup', methods=['POST'])
def signup():
    # Parse user data, hash password, save to DB, return JWT
    return jsonify({'status': 'success', 'message': 'User created.'})
