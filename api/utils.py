import logging

import fastapi
import fastapi.security as security
import jose

from api.constants import TokenType

logger = logging.getLogger(__name__)


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
