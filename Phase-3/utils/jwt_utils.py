import jwt
import datetime
from config import Config

def create_jwt(payload, exp_minutes=60):
    payload = payload.copy()
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes)
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
