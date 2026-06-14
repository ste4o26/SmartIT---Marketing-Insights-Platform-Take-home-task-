import logging

import fastapi
import fastapi.responses as responses
import pydantic
from api.exceptions import ApiError, InternalServiceError
from common.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


def register_middlewares(app: fastapi.FastAPI) -> None:
    app.exception_handler(pydantic.ValidationError)(handle_validation_error)
    app.exception_handler(ApiError)(handle_api_service_error)
    app.exception_handler(ServiceUnavailableError)(handle_service_unavailability_error)
    app.exception_handler(InternalServiceError)(handle_internal_service_error)
    app.exception_handler(Exception)(handle_unexpected_error)


async def handle_validation_error(
    request: fastapi.Request, e: ValueError
) -> responses.JSONResponse:
    logger.exception("Unprocessable data: %s", e)
    return responses.JSONResponse(
        status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(e)},
    )


async def handle_api_service_error(
    request: fastapi.Request, e: ApiError
) -> responses.JSONResponse:
    logger.warning("%s: %s", e.__class__.__name__, e)
    return responses.JSONResponse(status_code=e.status_code, content={"detail": str(e)})


async def handle_service_unavailability_error(
    request: fastapi.Request, e: ServiceUnavailableError
) -> responses.JSONResponse:
    logger.error("Service unavailable: %s", e)
    return responses.JSONResponse(
        status_code=fastapi.status.HTTP_502_BAD_GATEWAY, content={"detail": str(e)}
    )


async def handle_internal_service_error(
    request: fastapi.Request, e: ServiceUnavailableError
) -> responses.JSONResponse:
    logger.error("Internal service failure: %s", e)
    return responses.JSONResponse(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": str(e)}
    )



async def handle_unexpected_error(
    request: fastapi.Request, e: Exception
) -> responses.JSONResponse:
    logger.exception("Unhandled API error")
    return responses.JSONResponse(
        status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Unexpected API service error"},
    )
