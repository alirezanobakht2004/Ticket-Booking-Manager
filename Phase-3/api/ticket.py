import logging
from functools import wraps
from services.es_client import get_es_client, get_ticket_index_name
from flask import Blueprint, request, jsonify



from services.ticket_service import (
    search_tickets_service,
    get_ticket_details_service,
    check_cancellation_penalty_service,
    cancel_ticket_and_refund_service,
)

ticket_bp = Blueprint('ticket', __name__)
logger = logging.getLogger(__name__)


# -----------------------
# Utility Functions
# -----------------------
def _parse_bool(val: str) -> bool:
    """Parse boolean values from query parameters."""
    if val is None:
        return False
    return str(val).lower() in ("1", "true", "yes", "y", "on")


# -----------------------
# Authentication Decorator
# -----------------------
def login_required(f):
    """Simple decorator for testing; replace with real JWT auth in production."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = 2  # Example user_id for testing
        logging.info(f"Simulating login for user_id: {user_id}")
        return f(current_user_id=user_id, *args, **kwargs)
    return decorated_function


# -----------------------
# Route Handlers
# -----------------------
@ticket_bp.route('/search', methods=['GET'])
def search_tickets():
    """Search for tickets with various filters and pagination."""
    args = request.args

    # Required parameters
    origin_id = args.get('origin_id', type=int)
    destination_id = args.get('destination_id', type=int)
    travel_date = args.get('travel_date')  # Expect 'YYYY-MM-DD'
    
    # Optional filters
    vehicle_type = args.get('vehicle_type')  # 'plane'|'train'|'bus' or None
    min_price = args.get('min_price', type=float)
    max_price = args.get('max_price', type=float)
    company_name = args.get('company_name')
    departure_start = args.get('departure_start')  # 'HH:MM'
    departure_end = args.get('departure_end')      # 'HH:MM'
    travel_class = args.get('travel_class', type=int)

    # Pagination and engine toggle
    page = args.get('page', default=1, type=int)
    page_size = args.get('page_size', default=50, type=int)
    use_es = _parse_bool(args.get('use_es'))  # optional toggle for ES

    # Basic validation
    if not origin_id or not destination_id or not travel_date:
        return jsonify({
            'status': 'error', 
            'message': 'origin_id, destination_id and travel_date are required'
        }), 400

    # Normalize vehicle_type if present
    if vehicle_type:
        vehicle_type = vehicle_type.strip().lower()
        if vehicle_type not in ('plane', 'train', 'bus'):
            vehicle_type = None  # ignore unknown values

    # Clamp pagination
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 50
    if page_size > 200:
        page_size = 200

    try:
        tickets = search_tickets_service(
            origin_id=origin_id,
            destination_id=destination_id,
            travel_date=travel_date,
            vehicle_type=vehicle_type,
            min_price=min_price,
            max_price=max_price,
            company_name=company_name,
            departure_start=departure_start,
            departure_end=departure_end,
            travel_class=travel_class,
            page=page,
            page_size=page_size,
            prefer_es=use_es or True  # default to ES if available; set False to force SQL
        )
        return jsonify({
            'status': 'success',
            'tickets': tickets,
            'page': page,
            'page_size': page_size
        }), 200
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'status': 'error', 'message': 'Search failed'}), 500


@ticket_bp.route('/details/<int:ticket_id>', methods=['GET'])
def get_ticket_details(ticket_id):
    """Get detailed information about a specific ticket."""
    try:
        ticket = get_ticket_details_service(ticket_id)
        if not ticket:
            return jsonify({'status': 'error', 'message': 'Ticket not found'}), 404
        return jsonify({'status': 'success', 'ticket': ticket}), 200
    except Exception as e:
        logger.error(f"Error fetching ticket details {ticket_id}: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to load ticket details'}), 500


@ticket_bp.route('/cancel/check/<int:ticket_id>', methods=['GET'])
def check_cancellation_penalty(ticket_id):
    """Check cancellation penalty for a ticket without canceling it."""
    try:
        penalty_info = check_cancellation_penalty_service(ticket_id)
        # Keep response structure consistent
        return jsonify({'status': 'success', 'data': penalty_info}), 200
    except ValueError as e:
        msg = str(e)
        if "not found" in msg.lower():
            return jsonify({"status": "error", "message": msg}), 404
        return jsonify({"status": "error", "message": msg}), 400
    except Exception as e:
        logger.error(f"Error checking cancellation penalty for ticket {ticket_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500


@ticket_bp.route('/cancel/<int:ticket_id>', methods=['POST'])
@login_required
def cancel_ticket(current_user_id, ticket_id):
    """Finalizes the cancellation of a ticket and processes the refund."""
    try:
        result = cancel_ticket_and_refund_service(current_user_id, ticket_id)
        return jsonify({"status": "success", "data": result}), 200
    except PermissionError as e:
        return jsonify({"status": "error", "message": str(e)}), 403
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        logging.error(f"Error cancelling ticket {ticket_id} for user {current_user_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred during cancellation."}), 500
    
@ticket_bp.route('/suggest/company', methods=['GET'])   # note: uses ticket_bp (NOT tickets_bp)
def suggest_company():
    q = (request.args.get("q") or "").strip()
    size = int(request.args.get("size") or 6)

    if not q or len(q) < 2:
        return jsonify({"suggestions": []}), 200

    es = get_es_client()
    index = get_ticket_index_name()

    # 1) Filter docs that start with the prefix in either company_name or brand
    # 2) Aggregate top unique values from both fields
    body = {
        "size": 0,
        "query": {
            "bool": {
                "should": [
                    {"prefix": {"company_name.raw_ci": q.lower()}},
                    {"prefix": {"brand.raw": q}},
                ],
                "minimum_should_match": 1
            }
        },
        "aggs": {
            "company_suggest": {"terms": {"field": "company_name.raw", "size": size}},
            "brand_suggest":   {"terms": {"field": "brand.raw",         "size": size}},
        }
    }

    try:
        resp = es.search(index=index, body=body)
        comps  = [b["key"] for b in resp.get("aggregations", {}).get("company_suggest", {}).get("buckets", [])]
        brands = [b["key"] for b in resp.get("aggregations", {}).get("brand_suggest",   {}).get("buckets", [])]

        # Merge + de-dup while preserving order; trim to requested size
        seen, out = set(), []
        for name in comps + brands:
            if name and name not in seen:
                seen.add(name)
                out.append(name)
            if len(out) >= size:
                break

        return jsonify({"suggestions": out}), 200
    except Exception as e:
        # Don’t break the UI if ES hiccups
        logging.error(f"Suggest error: {e}")
        return jsonify({"suggestions": []}), 200