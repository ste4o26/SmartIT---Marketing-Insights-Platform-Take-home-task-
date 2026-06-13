import decimal

import pydantic

from common.utils import validate_symbol


class Ticker(pydantic.BaseModel):

    symbol: str
    last_price: decimal.Decimal = pydantic.Field(alias="lastPrice")
    price_change: decimal.Decimal = pydantic.Field(alias="priceChange")
    price_change_percent: decimal.Decimal = pydantic.Field(alias="priceChangePercent")
    weighted_average_price: decimal.Decimal = pydantic.Field(alias="weightedAvgPrice")
    high_price: decimal.Decimal = pydantic.Field(alias="highPrice")
    low_price: decimal.Decimal = pydantic.Field(alias="lowPrice")
    volume: decimal.Decimal
    quote_volume: decimal.Decimal = pydantic.Field(alias="quoteVolume")
    close_time: int = pydantic.Field(alias="closeTime")

    @pydantic.field_validator(
        "last_price",
        "weighted_average_price",
        "high_price",
        "low_price",
        "volume",
        "quote_volume",
    )
    @classmethod
    def validate_non_negative_decimal(cls, value: decimal.Decimal) -> decimal.Decimal:
        if value < 0:
            raise ValueError("Market data values cannot be negative")
        return value

    @pydantic.field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        return validate_symbol(value)
