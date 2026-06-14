import fastapi
import fastapi.security as security

from api.dtos.credential import Credential
from api.dtos.token import Token
from api.services.auth import AuthService

_bearer_scheme = security.HTTPBearer()
router = fastapi.APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/access-token", response_model=Token)
async def get_access_token(credentials: Credential):
    service = AuthService()
    return service.get_access_token(credentials)


@router.post("/refresh-access-token", response_model=Token)
async def refresh_access_token(
    credentials: security.HTTPAuthorizationCredentials = fastapi.Depends(
        _bearer_scheme
    ),
):
    service = AuthService()
    return service.refresh_access_token(credentials.credentials)
