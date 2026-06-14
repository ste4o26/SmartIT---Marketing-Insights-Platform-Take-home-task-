import datetime
import logging
import os
import typing

import jose
import jose.jwt as jwt

from common.constants import BEARER, DEFAULT_TOKEN_EXPIRY_SECONDS
from api.constants import TokenType, DEFAULT_REFRESH_TOKEN_EXPIRY_SECONDS
from api.dtos.credential import Credential
from api.dtos.token import Token

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
        except jose.JWTError as e:
            logger.exception("Authentication failed!")
            raise ValueError("Could not create authentication token") from e

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
        subject = self.validate_token(refresh_token, TokenType.REFRESH)
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

    def validate_token(self, token: str, token_type: TokenType) -> str:
        payload = jwt.decode(token, key=self._secret, algorithms=[self._algorithm])
        if TokenType(payload.get("token_type")) != token_type:
            raise ValueError(f"Expected {token_type} token")

        if not (subject := payload.get("sub")):
            raise ValueError("Token subject is missing")
        return subject

    def _create_token(self, subject: str, token_type: str, expires_in: int) -> str:
        payload = {
            "sub": subject,
            "token_type": token_type,
            "exp": datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(seconds=expires_in),
        }

        return jwt.encode(payload, key=self._secret, algorithm=self._algorithm)

    def _get_expiry_times(self) -> _ExpiryTimes:
        access_expires_in = int(
            os.getenv("TOKEN_EXPIRY_SECONDS") or DEFAULT_TOKEN_EXPIRY_SECONDS
        )
        refresh_expires_in = int(
            os.getenv("REFRESH_TOKEN_EXPIRY_SECONDS")
            or DEFAULT_REFRESH_TOKEN_EXPIRY_SECONDS
        )
        return _ExpiryTimes(access_expires_in, refresh_expires_in)
