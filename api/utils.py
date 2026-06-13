import logging

import fastapi
import fastapi.security as security
import jose

from api.constants import TokenType

logger = logging.getLogger(__name__)


def set_cookie(
    response: fastapi.Response, *, key: str, value: str, expires_in: int | None = None
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=expires_in,
        httponly=True,
        secure=False,
        samesite="lax",
    )


_oauth2_scheme = security.OAuth2PasswordBearer(tokenUrl="/api/auth/access-token")


def get_user_subject(token: str = fastapi.Depends(_oauth2_scheme)) -> str:
    from api.services.auth import AuthService

    service = AuthService()
    try:
        return service.validate_token(token, TokenType.ACCESS)
    except (jose.JWTError, ValueError) as e:
        logger.error("Invalid auth token")
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth token",
        ) from e
