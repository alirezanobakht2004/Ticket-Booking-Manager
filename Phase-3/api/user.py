from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from services.user_service import get_user_bookings_service
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile/update', methods=['POST'])
def update_profile():
    return jsonify({'status': 'success', 'message': 'Profile updated.'})

# Similar stubs for ticket.py, admin.py, cities.py
################################################################

# --- NEW AND IMPROVED AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In a real app, you would decode a JWT here to get the user's ID.
        # For testing, we will hardcode a user_id.
        user_id = 2  # Example user_id.
        logging.info(f"Simulating login for user_id: {user_id}")
        
        # We pass the user_id as a new keyword argument to the decorated function
        return f(current_user_id=user_id, *args, **kwargs)
    return decorated_function


# The function now accepts 'current_user_id' as a parameter
@user_bp.route('/bookings', methods=['GET'])
@login_required
def get_my_bookings(current_user_id):
    """
    Fetches the logged-in user's tickets, with an optional filter.
    Filter can be 'upcoming', 'past', or 'cancelled'.
    """
    # The filter is passed as a query parameter, e.g., ?filter=upcoming
    filter_type = request.args.get('filter', 'upcoming') # Default to 'upcoming'

    try:
        # We now use the user_id passed directly from the decorator
        bookings = get_user_bookings_service(current_user_id, filter_type)
        return jsonify(bookings), 200
        
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 404
    except Exception as e:
        logging.error(f"Error fetching bookings for user {current_user_id}: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred."}), 500
