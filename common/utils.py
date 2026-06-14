import functools
import inspect
import logging
import typing

import fastapi
import fastapi.security as security
import httpx

from common.constants import InternalService, SYMBOL_PATTERN
from common.exceptions import S2SAuthenticationError, ServiceUnavailableError

logger = logging.getLogger(__name__)


def validate_symbol(value: str) -> str:
    symbol = value.strip().upper()
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise ValueError("Symbol must contain 3-20 uppercase letters or numbers")
    return symbol


def session(
    func: typing.Callable[..., typing.Awaitable[typing.Any]] | None = None,
    *,
    base_url: str = "",
    timeout: float | None = None,
) -> typing.Any:
    """Wraps the decorated function around httpx.AsyncClient and injects it."""

    def _decorator(
        fn: typing.Callable[..., typing.Awaitable[typing.Any]],
    ) -> typing.Callable[..., typing.Awaitable[typing.Any]]:
        params = list(inspect.signature(fn).parameters)
        is_method = bool(params and params[0] in {"self", "cls"})

        @functools.wraps(fn)
        async def _wrap(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            try:
                async with httpx.AsyncClient(
                    base_url=base_url, timeout=timeout
                ) as session:
                    if is_method:
                        self_or_cls, *rest = args
                        return await fn(self_or_cls, session, *rest, **kwargs)
                    return await fn(session, *args, **kwargs)
            except httpx.ConnectError as e:
                logger.error("The respective service is down: %s", base_url)
                raise ServiceUnavailableError(
                    f"Service at {base_url or '<missing base url>'} is unavailable"
                ) from e

        return _wrap

    if func is not None:
        return _decorator(func)

    return _decorator


_bearer_scheme = security.HTTPBearer()


def get_service_subject(
    *,
    audience: InternalService,
    allowed_issuers: list[InternalService] | None = None,
) -> typing.Callable:
    from common.services.auth import AuthS2S

    if not allowed_issuers:
        raise S2SAuthenticationError(
            f"Service {audience} isn't setup to interact with other internal services"
        )

    try:
        service = AuthS2S()
    except ValueError as e:
        raise S2SAuthenticationError(
            "Service to Service authentication flow isn't fully setup"
        ) from e

    def wrap(
        credentials: security.HTTPAuthorizationCredentials = fastapi.Depends(
            _bearer_scheme
        ),
    ) -> str:
        token = credentials.credentials
        for issuer in allowed_issuers:
            try:
                return service.validate_service_token(
                    token, issuer=issuer, audience=audience
                )
            except (S2SAuthenticationError, ValueError):
                logger.exception(
                    "Internal service token validation failed for issuer %s audience %s",
                    issuer,
                    audience,
                )

        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Internal service to service token validation failed",
        )

    return wrap
