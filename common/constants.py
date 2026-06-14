import enum
import re

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{3,20}$")
DEFAULT_TOKEN_EXPIRY_SECONDS = "600"
BEARER = "Bearer"


class InternalService(enum.StrEnum):
    API = "api-service"
    MARKET_DATA = "market-data-service"
