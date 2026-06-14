import enum

SERVICE_URI_PREFIX = "api"
DEFAULT_REFRESH_TOKEN_EXPIRY_SECONDS = "6000"


class TokenType(enum.StrEnum):

    ACCESS = enum.auto()
    REFRESH = enum.auto()
