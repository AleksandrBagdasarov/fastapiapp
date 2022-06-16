import jwt
import time
from conf import JWT_SECRET, JWT_ALGORITHM, MASTER_SECRET_KEY, SALT
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db.redis_processor import MyRedis
import bcrypt

redis = MyRedis()


async def get_hashed_pwd(password):
    combo_password = (password + MASTER_SECRET_KEY + password[:4]).encode("utf-8")
    hashed_password = (bcrypt.hashpw(combo_password, SALT.encode("utf-8"))).decode("utf-8")
    return hashed_password


async def sign_jwt(user_id: str):
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token
    except:
        return {}


def token_from_request(request: Request) -> str:
    token = request.headers["authorization"].replace("Bearer ", "")
    return token


async def remove_token(request: Request) -> None:
    token = token_from_request(request)
    if token:
        payload = decode_jwt(token)
        user_id = payload["user_id"]
        await redis.remove(user_id)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not await self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    @staticmethod
    async def verify_jwt(token: str) -> bool:
        is_token_valid: bool = False

        try:
            payload = decode_jwt(token)
            user_id = payload["user_id"]
            redis_exist_user_id = await redis.get(user_id)
            assert token == redis_exist_user_id["token"]
            assert payload["expires"] >= time.time()
            assert redis_exist_user_id.get("blocked") is None
        except Exception as e:
            payload = None
        if payload:
            is_token_valid = True
        return is_token_valid
