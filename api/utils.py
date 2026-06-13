import fastapi
import fastapi.security as security

from api.constants import TokenType


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


def get_current_user_id(token: str = fastapi.Depends(_oauth2_scheme)) -> str:
    from api.services.auth import AuthService

    service = AuthService()
    return service.validate_token(token, TokenType.ACCESS)
