from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.core.config import settings
from app.schemas.auth import TokenCreateData, TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: TokenCreateData):
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    pyload = {
        "sub": str(data.user_id),
        "role": data.role,
        "exp": expire,
    }
    return jwt.encode(pyload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> TokenPayload | None:
    try:
        print("TOKEN RECEIVED:", repr(token))

        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        return payload

    except InvalidTokenError as e:
        print(f"Invalid token error: {str(e)}")
        return None