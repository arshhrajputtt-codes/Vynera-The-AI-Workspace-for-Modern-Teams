from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import InvalidTokenError


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise InvalidTokenError() from exc
