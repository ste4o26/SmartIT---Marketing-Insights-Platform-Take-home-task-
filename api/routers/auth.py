import fastapi
import fastapi.security as security
import jose

from api.constants import ACCESS_TOKEN_COOKIE_NAME, REFRESH_TOKEN_COOKIE_NAME
from api.dtos.credential import Credential
from api.dtos.token import Token
from api.services.auth import AuthService
from api.utils import set_cookie

_bearer_scheme = security.HTTPBearer()
router = fastapi.APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/access-token", response_model=Token)
async def get_access_token(credentials: Credential, response: fastapi.Response):
    service = AuthService()
    try:
        token = service.get_access_token(credentials)
    except (jose.JWTError, ValueError) as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e

    if token:
        set_cookie(
            response,
            key=ACCESS_TOKEN_COOKIE_NAME,
            value=token.access_token,
            expires_in=token.expires_in,
        )
    if token and token.refresh_token:
        set_cookie(
            response,
            key=REFRESH_TOKEN_COOKIE_NAME,
            value=token.refresh_token,
            expires_in=token.refresh_expires_in,
        )
    return token


@router.post("/refresh-access-token", response_model=Token)
async def refresh_access_token(
    response: fastapi.Response,
    credentials: security.HTTPAuthorizationCredentials = fastapi.Depends(
        _bearer_scheme
    ),
):
    service = AuthService()
    try:
        token = service.refresh_access_token(credentials.credentials)
    except (jose.JWTError, ValueError) as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e

    if token.access_token:
        set_cookie(
            response,
            key=ACCESS_TOKEN_COOKIE_NAME,
            value=token.access_token,
            expires_in=token.expires_in,
        )
    return token
