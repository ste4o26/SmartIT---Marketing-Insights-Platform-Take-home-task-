import enum

SERVICE_URI_PREFIX = "api"
DEFAULT_TOKEN_EXPIRY_TIME_IN_SECONDS = "6000"
DEFAULT_REFRESH_TOKEN_EXPIRY_TIME_IN_SECONDS = "604800"

BEARER = "Bearer"
ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"


class TokenType(enum.StrEnum):

    ACCESS = enum.auto()
    REFRESH = enum.auto()
