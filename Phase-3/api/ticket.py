from flask import Blueprint, request, jsonify
from services.ticket_service import search_tickets_service

ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/tickets/search', methods=['GET'])
def search_tickets():
    args = request.args

    origin_id = args.get('origin_id', type=int)
    destination_id = args.get('destination_id', type=int)
    travel_date = args.get('travel_date')  # Expect 'YYYY-MM-DD'
    vehicle_type = args.get('vehicle_type')  # 'plane', 'train', 'bus' or None
    min_price = args.get('min_price', type=float)
    max_price = args.get('max_price', type=float)
    company_name = args.get('company_name')
    departure_start = args.get('departure_start')  # 'HH:MM'
    departure_end = args.get('departure_end')      # 'HH:MM'
    travel_class = args.get('travel_class', type=int)

    # Basic validation
    if not origin_id or not destination_id or not travel_date:
        return jsonify({'status': 'error', 'message': 'origin_id, destination_id and travel_date are required'}), 400

    results = search_tickets_service(
        origin_id, destination_id, travel_date, vehicle_type,
        min_price, max_price, company_name,
        departure_start, departure_end, travel_class
    )

    return jsonify({'status': 'success', 'tickets': results})

from flask import Blueprint, jsonify, abort
from services.ticket_service import get_ticket_details_service

ticket_bp = Blueprint('ticket', __name__)

@ticket_bp.route('/tickets/details/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    ticket = get_ticket_details_service(ticket_id)
    if not ticket:
        return jsonify({'status': 'error', 'message': 'Ticket not found'}), 404
    return jsonify({'status': 'success', 'ticket': ticket})
