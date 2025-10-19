import datetime
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from db.db import (
    get_reservation_by_ticket_id,
    get_ticket_details,
    get_ticket_for_cancellation_check,
    get_ticket_owner_person_id,
    search_tickets as search_tickets_sql,
    update_reservation_status,
    add_to_user_wallet,
)
from services.cache_service import get_cached_search, cache_search

# ES client is optional; if not present or fails, we fall back to SQL
try:
    from services.es_client import search_tickets_es
    ES_AVAILABLE = True
except Exception:
    ES_AVAILABLE = False

logger = logging.getLogger(__name__)


# -----------------------
# Caching Helpers
# -----------------------
def generate_cache_key(params: dict, engine: str = "sql") -> str:
    """
    Create a stable cache key for search params.
    engine: 'sql' or 'es' to namespace and allow side-by-side testing.
    """
    key_str = json.dumps(params, sort_keys=True, default=str)
    digest = hashlib.md5(key_str.encode("utf-8")).hexdigest()
    return f"search_tickets:{engine}:{digest}"


# -----------------------
# Serialization Helpers
# -----------------------
def serialize_datetimes(obj: Any) -> Any:
    """
    Recursively convert datetime objects to ISO8601 strings.
    """
    if isinstance(obj, list):
        return [serialize_datetimes(item) for item in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(v, (datetime.datetime, datetime.date)):
                out[k] = v.isoformat()
            else:
                out[k] = serialize_datetimes(v)
        return out
    return obj


# -----------------------
# Result Normalization Functions
# -----------------------
def normalize_sql_results(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize SQL rows returned by db.search_tickets to the payload your API uses.
    This simply returns rows as-is (they already match what your Android expects),
    but you can map/rename keys here if needed.
    """
    return rows or []


def normalize_es_results(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize ES documents into the same shape as SQL output expected by the client:
      - ticket_id, source, destination, departure_time, arrival_time,
        price, class_code, brand, model,
        bus_company, airline_name, train_type
    ES docs come from es_client.normalize_ticket_doc() and get_all_tickets_for_indexing().
    """
    norm: List[Dict[str, Any]] = []
    for d in rows or []:
        norm.append({
            "ticket_id": d.get("ticket_id"),
            "source": d.get("origin_id"),
            "destination": d.get("destination_id"),
            "departure_time": d.get("departure_time"),
            "arrival_time": d.get("arrival_time"),
            "price": d.get("price"),
            "class_code": d.get("class_code"),
            "brand": d.get("brand"),
            "model": d.get("model"),
            # Map company_name back into the three columns clients expect
            "bus_company": d.get("company_name") if d.get("vehicle_type") == "bus" else None,
            "airline_name": d.get("company_name") if d.get("vehicle_type") == "plane" else None,
            "train_type": d.get("company_name") if d.get("vehicle_type") == "train" else None,
        })
    return norm


# -----------------------
# Search Service (ES + SQL Fallback)
# -----------------------
def search_tickets_service(
    origin_id: int,
    destination_id: int,
    travel_date: str,
    vehicle_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    company_name: Optional[str] = None,
    departure_start: Optional[str] = None,
    departure_end: Optional[str] = None,
    travel_class: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
    prefer_es: bool = True,
) -> List[Dict[str, Any]]:
    """
    Unified search service:
    - Tries ElasticSearch first if available and prefer_es=True (default)
    - Falls back to SQL on any error or if ES is disabled
    - Uses Redis cache for final normalized payload
    """
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
        "travel_class": travel_class,
        "page": page,
        "page_size": page_size,
    }

    # Attempt ES path
    if ES_AVAILABLE and prefer_es:
        cache_key_es = generate_cache_key(params, engine="es")
        cached = get_cached_search(cache_key_es)
        if cached is not None:
            return cached

        try:
            es_resp = search_tickets_es(params, page=page, page_size=page_size)
            es_docs = es_resp.get("results", [])
            normalized = normalize_es_results(es_docs)
            # Serialize and cache
            norm_serializable = serialize_datetimes(normalized)
            cache_search(cache_key_es, norm_serializable)
            return norm_serializable
        except Exception as e:
            logger.error(f"ES search failed, using SQL fallback: {e}")

    # SQL path (fallback or preference)
    cache_key_sql = generate_cache_key(params, engine="sql")
    cached_sql = get_cached_search(cache_key_sql)
    if cached_sql is not None:
        return cached_sql

    rows = search_tickets_sql(
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
    )

    normalized_sql = normalize_sql_results(rows)
    norm_serializable = serialize_datetimes(normalized_sql)
    cache_search(cache_key_sql, norm_serializable)
    return norm_serializable


# -----------------------
# Ticket Details Service
# -----------------------
def get_ticket_details_service(ticket_id: int) -> Optional[Dict[str, Any]]:
    ticket = get_ticket_details(ticket_id)
    if not ticket:
        return None
    capacity = ticket.get("capacity")
    reserved_number = ticket.get("reserved_number") or 0
    remaining_capacity = (capacity - reserved_number) if capacity is not None else None
    ticket["remaining_capacity"] = remaining_capacity
    return ticket


# -----------------------
# Cancellation Penalty Service
# -----------------------
def check_cancellation_penalty_service(ticket_id: int) -> Dict[str, Any]:
    """
    Checks the cancellation penalty for a given ticket without performing the cancellation.
    Raises ValueError if not cancellable.
    """
    ticket = get_ticket_for_cancellation_check(ticket_id)
    if not ticket:
        raise ValueError("Ticket not found.")

    if ticket.get("reservation_status") != "CONFIRMED":
        raise ValueError(f"Ticket is not in a cancellable state. Current status: {ticket.get('reservation_status')}")

    now_utc = datetime.datetime.utcnow()
    departure_time = ticket.get("departure_time")
    if isinstance(departure_time, str):
        # If your DB returns strings here, parse to datetime; otherwise it may already be a datetime
        try:
            departure_time = datetime.datetime.fromisoformat(departure_time.replace("Z", ""))
        except Exception:
            # If parsing fails, treat as not cancellable to be safe
            raise ValueError("Invalid departure time format.")
    if not isinstance(departure_time, datetime.datetime):
        raise ValueError("Invalid departure time.")

    if now_utc >= departure_time:
        raise ValueError("This ticket cannot be cancelled as the departure time has passed.")

    time_remaining = departure_time - now_utc
    hours_remaining = time_remaining.total_seconds() / 3600.0

    penalty_percentage = 0
    vehicle_type = ticket.get("vehicle_type")

    if vehicle_type == "plane":
        if hours_remaining > 24:
            penalty_percentage = 10
        elif 12 <= hours_remaining <= 24:
            penalty_percentage = 30
        else:
            penalty_percentage = 50
    elif vehicle_type in ["bus", "train"]:
        if hours_remaining > 8:
            penalty_percentage = 5
        elif 3 <= hours_remaining <= 8:
            penalty_percentage = 15
        else:
            penalty_percentage = 40
    else:
        penalty_percentage = 100

    ticket_price = float(ticket.get("price") or 0.0)
    penalty_amount = (ticket_price * penalty_percentage) / 100.0
    refundable_amount = ticket_price - penalty_amount

    return {
        "ticket_id": ticket_id,
        "ticket_price": round(ticket_price, 2),
        "departure_time": departure_time.isoformat() + "Z",
        "hours_remaining": round(hours_remaining, 2),
        "penalty_percentage": penalty_percentage,
        "penalty_amount": round(penalty_amount, 2),
        "refundable_amount": round(refundable_amount, 2),
    }


# -----------------------
# Cancel + Refund Service
# -----------------------
def cancel_ticket_and_refund_service(current_user_id: int, ticket_id: int) -> Dict[str, Any]:
    """
    Cancels a ticket (by cancelling its reservation) and refunds the user per penalty rules.
    """
    ticket_owner_id = get_ticket_owner_person_id(ticket_id)
    if not ticket_owner_id or ticket_owner_id != current_user_id:
        raise PermissionError("You do not have permission to cancel this ticket.")

    try:
        penalty_info = check_cancellation_penalty_service(ticket_id)
        refundable_amount = penalty_info["refundable_amount"]
    except ValueError as e:
        raise ValueError(f"Ticket cancellation failed: {str(e)}") from e

    reservation = get_reservation_by_ticket_id(ticket_id)
    if not reservation:
        raise ValueError("Could not find reservation for this ticket.")
    reservation_id = reservation["reservation_id"]

    if not update_reservation_status(reservation_id, "CANCELLED"):
        raise Exception("Failed to update reservation status.")

    if refundable_amount > 0:
        if not add_to_user_wallet(current_user_id, refundable_amount):
            logging.critical(
                "CRITICAL: User %s was not refunded %s for cancelled reservation %s.",
                current_user_id, refundable_amount, reservation_id
            )
            raise Exception("Cancellation was successful, but a refund processing error occurred. Please contact support.")

    return {
        "message": "Ticket cancelled successfully.",
        "reservation_id": reservation_id,
        "refunded_amount": refundable_amount,
    }