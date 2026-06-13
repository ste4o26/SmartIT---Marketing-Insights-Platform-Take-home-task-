import datetime
import decimal
import logging
import os
import typing

import cachetools

from common.dtos.signal import Signal
from common.dtos.ticker import Ticker
from common.utils import validate_symbol
from market_data.clients.binance import BinanceMarketDataClient
from market_data.constants import (
    DEFAULT_TICKER_CACHE_MAX_SIZE,
    DEFAULT_TICKER_CACHE_TTL_SECONDS,
    FULL_CONFIDENCE_CHANGE_PERCENT,
    PERCENT_THRESHOLD,
    SignalType,
)

logger = logging.getLogger(__name__)

_TICKER_CACHE = cachetools.TTLCache(
    maxsize=int(os.getenv("TICKER_CACHE_MAX_SIZE") or DEFAULT_TICKER_CACHE_MAX_SIZE),
    ttl=int(os.getenv("TICKER_CACHE_TTL_SECONDS") or DEFAULT_TICKER_CACHE_TTL_SECONDS),
)


class CryptoMarketDataService:

    def __init__(self, client: BinanceMarketDataClient | None = None):
        self._client = client or BinanceMarketDataClient()

    async def get_ticker(self, symbol: str) -> Ticker:
        symbol = validate_symbol(symbol)
        if ticker := typing.cast(Ticker, _TICKER_CACHE.get(symbol)):
            logger.info("Returning ticker from cache for symbol %s", symbol)
            return ticker

        ticker = await self._client.get_ticker(symbol)
        _TICKER_CACHE[symbol] = ticker
        return ticker

    async def get_signal(self, symbol: str) -> Signal:
        ticker = await self.get_ticker(symbol)
        change_percent = ticker.price_change_percent
        signal_type = self._get_signal_type(change_percent)
        confidence = abs(change_percent) / FULL_CONFIDENCE_CHANGE_PERCENT
        confidence = float(min(confidence, decimal.Decimal(1)))
        return Signal.model_validate(
            {
                "symbol": ticker.symbol,
                "signal": signal_type,
                "confidence": confidence,
                "price": ticker.last_price,
                "price_change_percent_24h": ticker.price_change_percent,
                "source": "binance",
                "generated_at": datetime.datetime.now(datetime.UTC),
            }
        )

    def _get_signal_type(self, value: decimal.Decimal) -> SignalType:
        if abs(value) < PERCENT_THRESHOLD:
            return SignalType.NEUTRAL
        return SignalType.BULLISH if value > 0 else SignalType.BEARISH
