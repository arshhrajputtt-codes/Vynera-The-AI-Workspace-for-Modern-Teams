from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import InvalidTokenError
from app.core.jwt import decode_access_token

security = HTTPBearer()


@dataclass
class CurrentUser:
    """
    Lightweight stand-in for the User row core-service doesn't have. Only
    carries what identity-service put in the JWT claims.
    """

    id: int
    email: str
    token: str  # raw bearer token, forwarded to identity-service for role checks


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = payload.get("user_id")
    email = payload.get("email")

    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required claims",
        )

    return CurrentUser(id=user_id, email=email, token=credentials.credentials)
