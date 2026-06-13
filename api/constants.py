import enum

SERVICE_URI_PREFIX = "api"

DEFAULT_REFRESH_TOKEN_EXPIRY_SECONDS = "6000"
ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"


class TokenType(enum.StrEnum):

    ACCESS = enum.auto()
    REFRESH = enum.auto()
