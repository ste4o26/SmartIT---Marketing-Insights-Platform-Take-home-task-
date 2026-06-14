import fastapi


class ServiceUnavailableError(Exception):
    """Raised when an HTTP service dependency cannot be reached."""


class UnsupportedS2SIntegrationError(Exception):
    """Raised when service to service setup is not configured. I.e. missing client id/secret"""


class S2SAuthenticationError(Exception):
    """Raised when service tries to authenticate with invalid token"""

    def __init__(
        self, *args, status_code: int = fastapi.status.HTTP_401_UNAUTHORIZED
    ) -> None:
        self.status_code = status_code
        super().__init__(*args)
