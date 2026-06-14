import logging

import fastapi
from fastapi.responses import JSONResponse
import pydantic

from common.exceptions import ServiceUnavailableError
from market_data.exceptions import MarketDataError

logger = logging.getLogger(__name__)


def register_middlewares(app: fastapi.FastAPI) -> None:
    app.exception_handler(pydantic.ValidationError)(handle_value_error)
    app.exception_handler(MarketDataError)(handle_market_data_error)
    app.exception_handler(ServiceUnavailableError)(handle_service_unavailability_error)
    app.exception_handler(Exception)(handle_unexpected_error)


async def handle_value_error(request: fastapi.Request, e: ValueError) -> JSONResponse:
    logger.exception("Unprocessable data: %s", e)
    return JSONResponse(
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(e)},
    )


async def handle_market_data_error(
    request: fastapi.Request, e: MarketDataError
) -> JSONResponse:
    logger.exception("%s: %s", e.__class__.__name__, e)
    return JSONResponse(status_code=e.status_code, content={"detail": str(e)})


async def handle_service_unavailability_error(
    request: fastapi.Request, e: ServiceUnavailableError
) -> JSONResponse:
    logger.error("Service unavailable: %s", e)
    return JSONResponse(
        status_code=fastapi.status.HTTP_502_BAD_GATEWAY, content={"detail": str(e)}
    )


async def handle_unexpected_error(
    request: fastapi.Request, e: Exception
) -> JSONResponse:
    logger.exception("Unhandled market-data service error %s", e)
    return JSONResponse(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Unexpected market-data service error"},
    )
