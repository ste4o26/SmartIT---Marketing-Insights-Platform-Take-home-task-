import fastapi
import fastapi.security as security
import jose

from api.dtos.credential import Credential
from api.dtos.token import Token
from api.services.auth import AuthService

_bearer_scheme = security.HTTPBearer()
router = fastapi.APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/access-token", response_model=Token)
async def get_access_token(credentials: Credential):
    service = AuthService()
    try:
        return service.get_access_token(credentials)
    except (jose.JWTError, ValueError) as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password",
        ) from e


@router.post("/refresh-access-token", response_model=Token)
async def refresh_access_token(
    credentials: security.HTTPAuthorizationCredentials = fastapi.Depends(
        _bearer_scheme
    ),
):
    service = AuthService()
    try:
        token = service.refresh_access_token(credentials.credentials)
    except (jose.JWTError, ValueError) as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from e
    return token
