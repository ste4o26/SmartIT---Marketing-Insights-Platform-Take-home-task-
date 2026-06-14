import logging
import os

import httpx
import pydantic

from common.dtos.ticker import Ticker
from common.exceptions import ServiceUnavailableError
from market_data.exceptions import (
    MarketDataFormatMismatchError,
    MarketDataProviderError,
    MarketDataSymbolNotFoundError,
)
from common.utils import session

logger = logging.getLogger(__name__)

_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
_TRACKER_URI = os.getenv("BINANCE_TRACKER_URI", "/api/v3/ticker/24hr")
_TIMEOUT = float(os.getenv("BINANCE_REQUEST_TIMEOUT_SECONDS", "5"))


class BinanceMarketDataClient:

    @session(base_url=_BASE_URL, timeout=_TIMEOUT)
    async def get_ticker(self, session: httpx.AsyncClient, symbol: str) -> Ticker:
        symbol = symbol.upper()
        try:
            response = await session.get(_TRACKER_URI, params={"symbol": symbol})
        except ServiceUnavailableError as e:
            logger.error("Binance request failed for symbol %s", symbol)
            raise MarketDataProviderError("Binance market data request failed") from e

        if response.is_error:
            if response.status_code == httpx.codes.BAD_REQUEST:
                logger.error("Binance rejected symbol %s", symbol)
                raise MarketDataSymbolNotFoundError(
                    f"Symbol {symbol} was not found by Binance"
                )

            logger.error(
                "Binance returned status %s for symbol %s",
                response.status_code,
                symbol,
            )
            raise MarketDataProviderError(
                f"Binance provider failure: {response.status_code} - {response.reason_phrase}"
            )

        try:
            return Ticker.model_validate(response.json())
        except (ValueError, pydantic.ValidationError) as e:
            logger.error("Invalid ticker format for symbol %s", symbol)
            raise MarketDataFormatMismatchError(
                "Invalid Binance market data format"
            ) from e
