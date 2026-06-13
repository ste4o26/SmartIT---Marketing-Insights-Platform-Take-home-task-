import logging
import os
import typing

import httpx
import pydantic

from api.exceptions import UpstreamResourceNotFoundError, UpstreamServiceError
from common.dtos.signal import Signal
from common.dtos.ticker import Ticker
from common.utils import session

logger = logging.getLogger(__name__)

_BASE_URL = os.getenv("MARKET_DATA_SERVICE_BASE_URL", "")
_TIMEOUT = float(os.getenv("MARKET_DATA_REQUEST_TIMEOUT_IN_SECONDS", "5"))

_SIGNAL_URI = "/market-data/crypto/signals"
_TICKER_URI = "/market-data/crypto/prices"


class MarketDataClient:

    async def get_ticker(self, symbol: str) -> Ticker:
        data = await self._get(f"{_TICKER_URI}/{symbol}")
        try:
            return Ticker.model_validate(data)
        except pydantic.ValidationError as error:
            logger.exception(
                "Market-data service returned invalid ticker payload for symbol %s",
                symbol,
            )
            raise UpstreamServiceError("Invalid market-data ticker payload") from error

    async def get_signal(self, symbol: str) -> Signal:
        data = await self._get(f"{_SIGNAL_URI}/{symbol}")
        try:
            return Signal.model_validate(data)
        except pydantic.ValidationError as error:
            logger.exception(
                "Market-data service returned invalid signal payload for symbol %s",
                symbol,
            )
            raise UpstreamServiceError("Invalid market-data signal payload") from error

    @session(base_url=_BASE_URL, timeout=_TIMEOUT)
    async def _get(self, session: httpx.AsyncClient, uri: str) -> dict[str, typing.Any]:
        response = await session.get(uri)
        if response.is_error:
            logger.error("Upstream api call failure: %s", uri)
            if response.status_code == httpx.codes.NOT_FOUND:
                raise UpstreamResourceNotFoundError(
                    f"Market-data resource was not found on {uri}"
                )
            raise UpstreamServiceError(
                f"Market-data service failed {response.status_code} - {response.reason_phrase}"
            )
        return response.json()
