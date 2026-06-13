import datetime
import os

import jose.jwt as jwt

from common.constants import DEFAULT_TOKEN_EXPIRY_SECONDS, InternalService


def _encode_s2s_pair(*, issuer: InternalService, audience: InternalService) -> str:
    return f"{issuer}-{audience}".encode().hex()


def _get_s2s_secrets(*, issuer: InternalService, audience: InternalService) -> str:
    key = _encode_s2s_pair(issuer=issuer, audience=audience)
    if not (api_to_market_data_secret := os.getenv("API_TO_MARKET_DATA_CLIENT_SECRET")):
        raise ValueError("API_TO_MARKET_DATA_CLIENT_SECRET is not configured")

    map_ = {
        _encode_s2s_pair(
            issuer=InternalService.API, audience=InternalService.MARKET_DATA
        ): api_to_market_data_secret
    }
    return map_[key]


def _get_s2s_client_id(*, issuer: InternalService, audience: InternalService) -> str:
    key = _encode_s2s_pair(issuer=issuer, audience=audience)
    if not (api_to_market_data_client_id := os.getenv("API_TO_MARKET_DATA_CLIENT_ID")):
        raise ValueError("API_TO_MARKET_DATA_CLIENT_ID is not configured")

    map_ = {
        _encode_s2s_pair(
            issuer=InternalService.API, audience=InternalService.MARKET_DATA
        ): api_to_market_data_client_id
    }
    return map_[key]


class AuthS2S:

    def __init__(self) -> None:
        if not (algorithm := os.getenv("AUTH_ALGORITHM")):
            raise ValueError("Authentication algorithm isn't setup!")
        self._algorithm = algorithm

    def get_service_token(
        self, *, issuer: InternalService, audience: InternalService
    ) -> str:
        client_id = _get_s2s_client_id(issuer=issuer, audience=audience)
        expires_in = int(
            os.getenv("TOKEN_EXPIRY_SECONDS") or DEFAULT_TOKEN_EXPIRY_SECONDS
        )
        payload = {
            "iss": issuer,
            "aud": audience,
            "sub": client_id,
            "client_id": client_id,
            "exp": datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=expires_in),
        }
        secret = _get_s2s_secrets(issuer=issuer, audience=audience)
        return jwt.encode(payload, key=secret, algorithm=self._algorithm)

    def validate_service_token(
        self, token: str, *, issuer: InternalService, audience: InternalService
    ) -> str:
        secret = _get_s2s_secrets(issuer=issuer, audience=audience)
        payload = jwt.decode(
            token,
            key=secret,
            algorithms=[self._algorithm],
            issuer=issuer,
            audience=audience,
        )
        return payload["sub"]
