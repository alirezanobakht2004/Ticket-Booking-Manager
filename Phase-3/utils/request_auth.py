from flask import request

from utils.jwt_utils import verify_jwt_token


def get_current_user_id_from_request():
    token = request.headers.get('Authorization')
    
    if not token:
        return None
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    data = verify_jwt_token(token)
    return data.get('user_id') if data else None