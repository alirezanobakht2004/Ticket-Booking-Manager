import jwt
import datetime
from config import Config

def create_jwt(payload, exp_minutes=60):
    payload = payload.copy()
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes)
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload  # Return the decoded token payload (includes user_id, email, etc.)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None