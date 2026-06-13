class ApiServiceError(Exception):
    """Base exception for API service failures."""


class UpstreamServiceError(ApiServiceError):
    """Raised when an upstream service cannot return usable data."""


class UpstreamResourceNotFoundError(ApiServiceError):
    """Raised when an upstream service cannot find the requested resource."""