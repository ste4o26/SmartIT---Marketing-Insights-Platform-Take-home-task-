import datetime
import decimal

import pydantic

from common.utils import validate_symbol


class Signal(pydantic.BaseModel):

    symbol: str
    signal_type: str
    confidence: float = pydantic.Field(ge=0, le=1)
    price: decimal.Decimal
    price_change_percent_24h: decimal.Decimal
    source: str
    generated_at: datetime.datetime

    @pydantic.field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        return validate_symbol(value)

    @pydantic.field_validator("price")
    @classmethod
    def validate_non_negative_decimal(cls, value: decimal.Decimal) -> decimal.Decimal:
        if value < 0:
            raise ValueError("Market data values cannot be negative")
        return value
