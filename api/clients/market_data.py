import logging
import os
import typing

import httpx
import pydantic

from api.exceptions import DataTransformationError, InternalServiceError
from common.dtos.signal import Signal
from common.dtos.ticker import Ticker
from common.exceptions import ServiceUnavailableError
from common.services.auth import AuthS2S
from common.constants import InternalService
from common.utils import session

logger = logging.getLogger(__name__)

_BASE_URL = os.getenv("MARKET_DATA_SERVICE_BASE_URL", "")
_TIMEOUT = float(os.getenv("MARKET_DATA_REQUEST_TIMEOUT_IN_SECONDS", "5"))

_SIGNAL_URI = "/market-data/crypto/signals"
_TICKER_URI = "/market-data/crypto/prices"


class MarketDataClient:

    async def get_ticker(self, symbol: str) -> Ticker:
        try:
            data = await self._get(f"{_TICKER_URI}/{symbol}")
        except ServiceUnavailableError as e:
            raise InternalServiceError("Market-data service is unavailable") from e

        try:
            return Ticker.model_validate(data)
        except pydantic.ValidationError as e:
            logger.exception(
                "Market-data service returned invalid ticker payload for symbol %s",
                symbol,
            )
            raise DataTransformationError(
                "Market-data service returned an invalid ticker payload"
            ) from e

    async def get_signal(self, symbol: str) -> Signal:
        try:
            data = await self._get(f"{_SIGNAL_URI}/{symbol}")
        except ServiceUnavailableError as e:
            raise InternalServiceError("Market-data service is unavailable") from e

        try:
            return Signal.model_validate(data)
        except pydantic.ValidationError as e:
            logger.exception(
                "Market-data service returned invalid signal payload for symbol %s",
                symbol,
            )
            raise DataTransformationError(
                "Market-data service returned an invalid signal payload"
            ) from e

    @session(base_url=_BASE_URL, timeout=_TIMEOUT)
    async def _get(self, session: httpx.AsyncClient, uri: str) -> dict[str, typing.Any]:
        service = AuthS2S()
        token = service.get_service_token(
            issuer=InternalService.API, audience=InternalService.MARKET_DATA
        )
        response = await session.get(uri, headers={"Authorization": f"Bearer {token}"})
        if response.is_error:
            message = self._get_http_error_message(response)
            logger.error("Market-data API call failed %s - %s", uri, message)
            raise InternalServiceError(
                f"Market-data service failed {response.status_code} - {message}",
                status_code=502,
            )
        return response.json()

    def _get_http_error_message(self, response: httpx.Response) -> str:
        try:
            data = response.json()
        except ValueError:
            return response.reason_phrase

        detail = data.get("detail")
        if isinstance(detail, str):
            return detail

        return str(detail or response.reason_phrase)
