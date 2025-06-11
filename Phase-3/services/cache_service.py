from db.redis_client import redis_client

OTP_TTL_SECONDS = 120  # 2 minutes, adjust as needed

def store_otp(user_key, otp_code, ttl=OTP_TTL_SECONDS):
    """Store OTP code in Redis with a TTL."""
    key = f"otp:{user_key}"
    redis_client.setex(key, ttl, otp_code)

def get_otp(user_key):
    """Retrieve OTP code from Redis."""
    key = f"otp:{user_key}"
    return redis_client.get(key)

def delete_otp(user_key):
    """Delete OTP code from Redis after use or expiry."""
    key = f"otp:{user_key}"
    redis_client.delete(key)
