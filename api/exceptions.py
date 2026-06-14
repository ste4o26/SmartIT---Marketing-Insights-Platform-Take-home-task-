import fastapi


class ApiError(Exception):
    """Base exception for API service failures."""

    def __init__(
        self, *args, status_code: int = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> None:
        self.status_code = status_code
        super().__init__(*args)


class AuthenticationError(ApiError):
    """Raised when user authentication fails."""

    def __init__(
        self, *args, status_code: int = fastapi.status.HTTP_401_UNAUTHORIZED
    ) -> None:
        super().__init__(*args, status_code=status_code)


class DataTransformationError(ApiError):
    """Raised when transforming from one data type to another fails."""


class InternalServiceError(Exception):
    """Raised when the API cannot get a usable response from market-data."""

    def __init__(
        self, *args, status_code: int = fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
    ) -> None:
        self.status_code = status_code
        super().__init__(*args)
