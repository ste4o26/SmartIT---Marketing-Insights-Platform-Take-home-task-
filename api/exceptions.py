class ApiServiceError(Exception):
    """Base exception for API service failures."""


class MarketDataApiError(ApiServiceError):
    """Raised when the API cannot get a usable response from market-data."""

    def __init__(self, message: str, *, status_code: int = 502) -> None:
        super().__init__(message)
        self.status_code = status_code
