import jwt
import datetime
from config import Config

def create_jwt(payload, exp_minutes=60):
    payload = payload.copy()
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes)
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import logging
from config import Config

def verify_jwt_token(token):
    try:
        # If token has 'Bearer ' prefix, remove it before decoding
        if token.startswith('Bearer '):
            token = token[7:]
        # Decode and verify the token using your secret key and algorithms
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        logging.debug(f"JWT payload decoded successfully: {payload}")
        return payload
    except ExpiredSignatureError:
        logging.error("JWT verification failed: Token has expired.")
        return None
    except InvalidTokenError as e:
        logging.error(f"JWT verification failed: Invalid token. Details: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error during JWT verification: {str(e)}")
        return None
