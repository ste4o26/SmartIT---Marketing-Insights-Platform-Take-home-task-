import datetime
import logging
import os
import typing

import jose
import jose.jwt as jwt

from api.constants import (
    BEARER,
    DEFAULT_REFRESH_TOKEN_EXPIRY_TIME_IN_SECONDS,
    DEFAULT_TOKEN_EXPIRY_TIME_IN_SECONDS,
    TokenType,
)
from api.dtos.credential import Credential
from api.dtos.token import Token

logger = logging.getLogger(__name__)


class _ExpiryTimes(typing.NamedTuple):
    access_token: int
    refresh_token: int


class AuthService:

    def get_access_token(self, credentials: Credential) -> Token | None:
        if not credentials.username or not credentials.password:
            raise ValueError("Username and password are required to authenticate!")

        expires_in, refresh_expires_in = self._get_expiry_times()
        try:
            access_token = self._create_token(
                subject=credentials.username,
                token_type="access",
                expires_in=expires_in,
            )
            refresh_token = self._create_token(
                subject=credentials.username,
                token_type="refresh",
                expires_in=refresh_expires_in,
            )
        except jose.JWTError:
            logger.exception("Authentication failed!")
            return None

        return Token.model_validate(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expires_in,
                "refresh_expires_in": refresh_expires_in,
                "token_type": BEARER,
            }
        )

    def refresh_access_token(self, refresh_token: str) -> Token:
        secret, algorithm = self._get_auth_settings()
        payload = jwt.decode(refresh_token, key=secret, algorithms=[algorithm])
        if TokenType(payload.get("token_type")) != TokenType.REFRESH:
            raise ValueError("Invalid refresh token!")

        if not (subject := payload.get("subject")):
            raise ValueError("Refresh token subject is missing!")

        print(TokenType(payload.get("token_type")))
        expires_in, _ = self._get_expiry_times()
        access_token = self._create_token(
            subject=subject, token_type=TokenType.ACCESS, expires_in=expires_in
        )

        return Token.model_validate(
            {
                "access_token": access_token,
                "expires_in": expires_in,
                "token_type": BEARER,
            }
        )

    def _create_token(self, subject: str, token_type: str, expires_in: int) -> str:
        secret, algorithm = self._get_auth_settings()
        payload = {
            "subject": subject,
            "token_type": token_type,
            "exp": datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=expires_in),
        }

        return jwt.encode(payload, key=secret, algorithm=algorithm)

    def _get_auth_settings(self) -> tuple[str, str]:
        if not (secret := os.getenv("AUTH_SECRET")):
            raise ValueError("Authentication secret isn't setup!")

        if not (algorithm := os.getenv("AUTH_ALGORITHM")):
            raise ValueError("Authentication algorithm isn't setup!")

        return secret, algorithm

    def _get_expiry_times(self) -> _ExpiryTimes:
        access_expires_in = int(
            os.getenv("TOKEN_EXPIRY_TIME_IN_SECONDS")
            or DEFAULT_TOKEN_EXPIRY_TIME_IN_SECONDS
        )
        refresh_expires_in = int(
            os.getenv("REFRESH_TOKEN_EXPIRY_TIME_IN_SECONDS")
            or DEFAULT_REFRESH_TOKEN_EXPIRY_TIME_IN_SECONDS
        )
        return _ExpiryTimes(access_expires_in, refresh_expires_in)
