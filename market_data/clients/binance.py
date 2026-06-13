import logging
import os

import httpx
import pydantic

from common.dtos.ticker import Ticker
from market_data.exceptions import (
    MarketDataFormatMismatchError,
    MarketDataProviderError,
)
from common.utils import session

logger = logging.getLogger(__name__)

_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
_TRACKER_URI = os.getenv("BINANCE_TRACKER_URI", "/api/v3/ticker/24hr")
_TIMEOUT = float(os.getenv("BINANCE_REQUEST_TIMEOUT_IN_SECONDS", "5"))


class BinanceMarketDataClient:

    @session(base_url=_BASE_URL, timeout=_TIMEOUT)
    async def get_ticker(self, session: httpx.AsyncClient, symbol: str) -> Ticker:
        symbol = symbol.upper()
        response = await session.get(_TRACKER_URI, params={"symbol": symbol})
        if response.is_error:
            logger.error("Invalid symbol %s", symbol)
            raise MarketDataProviderError(f"Binance rejected symbol {symbol}")

        try:
            return Ticker.model_validate(response.json())
        except (ValueError, pydantic.ValidationError) as e:
            logger.exception("Invalid ticker format for symbol %s", symbol)
            raise MarketDataFormatMismatchError(
                "Invalid Binance market data format"
            ) from e
