import decimal
import enum
import re

SERVICE_URI_PREFIX = "market-data"

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{3,20}$")

PERCENT_THRESHOLD = decimal.Decimal("2")
FULL_CONFIDENCE_CHANGE_PERCENT = decimal.Decimal("10")


class SignalPosition(enum.StrEnum):

    BULLISH = enum.auto()
    NEUTRAL = enum.auto()
    BEARISH = enum.auto()
