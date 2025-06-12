from flask import Blueprint, request, jsonify
from services.reservation_service import reserve_ticket_service, get_active_reservations_service, get_reservation_history_service
from utils.jwt_utils import verify_jwt_token

reservation_bp = Blueprint('reservation', __name__)

import logging

@reservation_bp.route('/reserve', methods=['POST'])
def reserve_ticket():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Authorization token required'}), 401
    if token.startswith('Bearer '):
        token = token[7:]
    user_data = verify_jwt_token(token)
    if not user_data:
        return jsonify({'status': 'error', 'message': 'Invalid or expired token'}), 401

    data = request.get_json()
    logging.debug(f"Reserve ticket request data: {data}, user_id: {user_data['user_id']}")

    ticket_id = data.get('ticket_id')
    validity_minutes = data.get('validity_minutes', 10)

    if not ticket_id:
        return jsonify({'status': 'error', 'message': 'ticket_id is required'}), 400

    reservation_id = reserve_ticket_service(user_data['user_id'], ticket_id, validity_minutes)
    logging.debug(f"Created reservation_id: {reservation_id} for user_id: {user_data['user_id']}")

    return jsonify({'status': 'success', 'reservation_id': reservation_id})

@reservation_bp.route('/active', methods=['GET'])
def active_reservations():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Authorization token required'}), 401
    if token.startswith('Bearer '):
        token = token[7:]
    user_data = verify_jwt_token(token)
    if not user_data:
        return jsonify({'status': 'error', 'message': 'Invalid or expired token'}), 401

    reservations = get_active_reservations_service(user_data['user_id'])
    return jsonify({'status': 'success', 'reservations': reservations})

@reservation_bp.route('/history', methods=['GET'])
def reservation_history():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'status': 'error', 'message': 'Authorization token required'}), 401
    if token.startswith('Bearer '):
        token = token[7:]
    user_data = verify_jwt_token(token)
    if not user_data:
        return jsonify({'status': 'error', 'message': 'Invalid or expired token'}), 401

    reservations = get_reservation_history_service(user_data['user_id'])
    return jsonify({'status': 'success', 'reservations': reservations})
