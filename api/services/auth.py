import datetime
import logging
import os
import typing

import fastapi
import jose
import jose.jwt as jwt

from api.constants import DEFAULT_REFRESH_TOKEN_EXPIRY_SECONDS, TokenType
from api.dtos.credential import Credential
from api.dtos.token import Token
from api.exceptions import AuthenticationError
from common.constants import BEARER, DEFAULT_TOKEN_EXPIRY_SECONDS

logger = logging.getLogger(__name__)


class _ExpiryTimes(typing.NamedTuple):
    access_token: int
    refresh_token: int


class AuthService:

    def __init__(self) -> None:
        if not (secret := os.getenv("AUTH_SECRET")):
            raise ValueError("Authentication secret isn't setup!")
        self._secret = secret

        if not (algorithm := os.getenv("AUTH_ALGORITHM")):
            raise ValueError("Authentication algorithm isn't setup!")
        self._algorithm = algorithm

    def get_access_token(self, credentials: Credential) -> Token:
        if not credentials.username or not credentials.password:
            raise AuthenticationError(
                "Invalid username or password",
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            )

        expirations = self._get_expiry_times()
        access_token = self._get_token(
            subject=credentials.username,
            token_type=TokenType.ACCESS,
            expires_in=expirations.access_token,
        )
        refresh_token = self._get_token(
            subject=credentials.username,
            token_type=TokenType.REFRESH,
            expires_in=expirations.refresh_token,
        )
        return Token.model_validate(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": expirations.access_token,
                "refresh_expires_in": expirations.refresh_token,
                "token_type": BEARER,
            }
        )

    def refresh_access_token(self, refresh_token: str) -> Token:
        try:
            subject = self.validate_token(refresh_token, TokenType.REFRESH)
        except (jose.JWTError, ValueError) as e:
            raise AuthenticationError("Invalid or expired refresh token") from e

        expirations = self._get_expiry_times()
        access_token = self._get_token(
            subject=subject,
            token_type=TokenType.ACCESS,
            expires_in=expirations.access_token,
        )
        return Token.model_validate(
            {
                "access_token": access_token,
                "expires_in": expirations.access_token,
                "token_type": BEARER,
            }
        )

    def validate_token(self, token: str, token_type: TokenType) -> str:
        try:
            payload = jwt.decode(token, key=self._secret, algorithms=[self._algorithm])
        except (
            jose.JWTError,
            jose.ExpiredSignatureError,
            jose.exceptions.JWTClaimsError,
        ) as e:
            raise AuthenticationError("Invalid or expired user auth token") from e

        subject = payload.get("sub")
        if not subject or TokenType(payload.get("token_type")) != token_type:
            raise AuthenticationError("Invalid user auth token")
        return subject

    def _get_token(self, subject: str, token_type: TokenType, expires_in: int) -> str:
        payload = {
            "sub": subject,
            "token_type": token_type,
            "exp": datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=expires_in),
        }
        try:
            return jwt.encode(payload, key=self._secret, algorithm=self._algorithm)
        except jose.JWTError as e:
            raise AuthenticationError(
                "Could not create authentication token",
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            ) from e

    def _get_expiry_times(self) -> _ExpiryTimes:
        access_expires_in = int(
            os.getenv("TOKEN_EXPIRY_SECONDS") or DEFAULT_TOKEN_EXPIRY_SECONDS
        )
        refresh_expires_in = int(
            os.getenv("REFRESH_TOKEN_EXPIRY_SECONDS")
            or DEFAULT_REFRESH_TOKEN_EXPIRY_SECONDS
        )
        return _ExpiryTimes(access_expires_in, refresh_expires_in)
