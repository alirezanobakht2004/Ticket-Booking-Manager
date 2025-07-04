from db.db import search_tickets
from services.cache_service import get_cached_search, cache_search
import hashlib
import json
from db.db import get_ticket_details


def generate_cache_key(params: dict) -> str:
    key_str = json.dumps(params, sort_keys=True)
    return "search_tickets:" + hashlib.md5(key_str.encode()).hexdigest()

import datetime

def serialize_datetimes(obj):
    if isinstance(obj, list):
        return [serialize_datetimes(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: (v.isoformat() if isinstance(v, datetime.datetime) else serialize_datetimes(v)) for k, v in obj.items()}
    else:
        return obj

def search_tickets_service(
    origin_id,
    destination_id,
    travel_date,
    vehicle_type=None,
    min_price=None,
    max_price=None,
    company_name=None,
    departure_start=None,
    departure_end=None,
    travel_class=None
):
    params = {
        "origin_id": origin_id,
        "destination_id": destination_id,
        "travel_date": travel_date,
        "vehicle_type": vehicle_type,
        "min_price": min_price,
        "max_price": max_price,
        "company_name": company_name,
        "departure_start": departure_start,
        "departure_end": departure_end,
        "travel_class": travel_class
    }

    cache_key = generate_cache_key(params)
    cached_result = get_cached_search(cache_key)
    if cached_result is not None:
        return cached_result

    results = search_tickets(
        origin_id=origin_id,
        destination_id=destination_id,
        travel_date=travel_date,
        vehicle_type=vehicle_type,
        min_price=min_price,
        max_price=max_price,
        company_name=company_name,
        departure_start=departure_start,
        departure_end=departure_end,
        travel_class=travel_class
    )

    # Serialize datetime objects before caching
    results_serializable = serialize_datetimes(results)

    cache_search(cache_key, results_serializable)
    return results_serializable



def get_ticket_details_service(ticket_id):
    ticket = get_ticket_details(ticket_id)
    if not ticket:
        return None
    # Optionally, compute remaining capacity
    remaining_capacity = ticket['capacity'] - ticket['reserved_number'] if ticket['capacity'] is not None else None
    ticket['remaining_capacity'] = remaining_capacity
    return ticket
