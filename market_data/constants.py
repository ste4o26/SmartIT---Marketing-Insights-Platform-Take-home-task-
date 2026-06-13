import decimal
import enum

SERVICE_URI_PREFIX = "market-data"

PERCENT_THRESHOLD = decimal.Decimal("2")
FULL_CONFIDENCE_CHANGE_PERCENT = decimal.Decimal("10")


class SignalType(enum.StrEnum):

    BULLISH = enum.auto()
    NEUTRAL = enum.auto()
    BEARISH = enum.auto()
