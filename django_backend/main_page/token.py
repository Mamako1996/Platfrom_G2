from jose import jwt
from datetime import datetime, timedelta
from jose.exceptions import ExpiredSignatureError, JWTError

SECRET_KEY = 'MuCSL'

EXPIRE_TIME = 1


def create_token(email):
    expire = datetime.utcnow() + timedelta(hours=EXPIRE_TIME)

    to_encode = {
        'exp': expire,
        'email': email
    }

    jwt_token = jwt.encode(claims=to_encode, key=SECRET_KEY, algorithm='HS256')
    return jwt_token


def check_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY)
        return payload
    except ExpiredSignatureError as e:
        return 'expired'
    except JWTError as e:
        return 'fail'


def token_auth(token):
    try:
        jwt.decode(token, SECRET_KEY)
        return True
    except:
        return False
