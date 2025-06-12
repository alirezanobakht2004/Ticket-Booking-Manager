from flask import Blueprint, jsonify
from services.cities_service import get_cities_service

cities_bp = Blueprint('cities', __name__)

@cities_bp.route('/cities', methods=['GET'])
def get_cities():
    cities = get_cities_service()
    return jsonify({'status': 'success', 'cities': cities})
