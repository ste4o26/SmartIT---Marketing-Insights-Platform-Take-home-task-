import decimal
import enum

SERVICE_URI_PREFIX = "market-data"
DEFAULT_TICKER_CACHE_MAX_SIZE = "500"
DEFAULT_TICKER_CACHE_TTL_SECONDS = "60"

PERCENT_THRESHOLD = decimal.Decimal("2")
FULL_CONFIDENCE_CHANGE_PERCENT = decimal.Decimal("10")


class SignalType(enum.StrEnum):

    BULLISH = enum.auto()
    NEUTRAL = enum.auto()
    BEARISH = enum.auto()
