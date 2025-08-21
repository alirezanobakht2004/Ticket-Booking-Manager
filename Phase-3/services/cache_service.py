import json
from typing import Any, Dict, Optional

from db.redis_client import redis_client

# Constants
OTP_TTL_SECONDS = 1200  # 20 minutes
TICKET_SEARCH_TTL = 300  # 5 minutes


# ---------------------------
# Utility Functions
# ---------------------------
def _bytes_to_str(b: Optional[bytes]) -> Optional[str]:
    """Convert Redis bytes response to string with fallback handling."""
    if b is None:
        return None
    try:
        return b.decode("utf-8")
    except Exception:
        # Fallback: treat as already str if decoding fails
        try:
            return str(b)
        except Exception:
            return None


def make_search_cache_key(prefix: str, key: str) -> str:
    """
    Compose a namespaced cache key for searches.
    Example: make_search_cache_key('search_tickets', computed_hash)
    """
    return f"{prefix}:{key}"


# ---------------------------
# OTP Management Functions
# ---------------------------
def store_otp(user_key: str, otp_code: str, ttl: int = OTP_TTL_SECONDS) -> None:
    """
    Store OTP code in Redis with a TTL.
    Key shape: otp:{user_key}
    """
    if not user_key or not otp_code:
        return
    key = f"otp:{user_key}"
    redis_client.setex(key, ttl, otp_code)


def get_otp(user_key: str) -> Optional[str]:
    """
    Retrieve OTP code from Redis.
    Returns the OTP string or None if not found/expired.
    """
    if not user_key:
        return None
    key = f"otp:{user_key}"
    raw = redis_client.get(key)
    return _bytes_to_str(raw)


def delete_otp(user_key: str) -> None:
    """
    Delete OTP code from Redis after use or expiry.
    """
    if not user_key:
        return
    key = f"otp:{user_key}"
    try:
        redis_client.delete(key)
    except Exception:
        # Non-fatal
        pass


# ---------------------------
# User Profile Cache Functions
# ---------------------------
def update_user_cache(
    user_id: int,
    first_name: Optional[str],
    last_name: Optional[str],
    phone_number: Optional[str],
    email: Optional[str],
    city: Optional[str],
    ttl: Optional[int] = None
) -> None:
    """
    Cache user profile as JSON. If ttl is provided, use setex; otherwise set without TTL.
    Key shape: user:{user_id}
    """
    if not user_id:
        return
    user_key = f"user:{user_id}"
    user_data: Dict[str, Any] = {
        "first_name": first_name,
        "last_name": last_name,
        "phone_number": phone_number,
        "email": email,
        "city": city
    }
    try:
        user_data_json = json.dumps(user_data, ensure_ascii=False)
        if ttl and ttl > 0:
            redis_client.setex(user_key, ttl, user_data_json)
        else:
            redis_client.set(user_key, user_data_json)
    except Exception:
        # Non-fatal
        pass


def get_user_cache(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch cached user profile.
    """
    if not user_id:
        return None
    user_key = f"user:{user_id}"
    raw = redis_client.get(user_key)
    s = _bytes_to_str(raw)
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def delete_user_cache(user_id: int) -> None:
    """
    Remove cached user profile (e.g., after profile update).
    """
    if not user_id:
        return
    user_key = f"user:{user_id}"
    try:
        redis_client.delete(user_key)
    except Exception:
        pass


# ---------------------------
# Ticket Search Cache Functions
# ---------------------------
def get_cached_search(key: str) -> Optional[Any]:
    """
    Read a cached search JSON payload by key.
    """
    if not key:
        return None
    raw = redis_client.get(key)
    s = _bytes_to_str(raw)
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return None


def cache_search(key: str, data: Any, ttl: int = TICKET_SEARCH_TTL) -> None:
    """
    Cache a search result as JSON under the given key for ttl seconds.
    """
    if not key:
        return
    try:
        payload = json.dumps(data, ensure_ascii=False)
        redis_client.setex(key, ttl, payload)
    except Exception:
        # Non-fatal
        pass


def delete_cached_search(key: str) -> None:
    """
    Invalidate a cached search entry.
    """
    if not key:
        return
    try:
        redis_client.delete(key)
    except Exception:
        pass