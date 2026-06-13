import functools
import inspect
import logging
import typing

import fastapi
import fastapi.security as security
import httpx
import jose

from common.constants import InternalService, SYMBOL_PATTERN

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
                raise RuntimeError(
                    "Requested resource couldn't be reached out because of service unavailability"
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

    service = AuthS2S()

    def wrap(
        credentials: security.HTTPAuthorizationCredentials = fastapi.Depends(
            _bearer_scheme
        ),
    ) -> str:
        token = credentials.credentials
        for issuer in allowed_issuers or []:
            try:
                return service.validate_service_token(
                    token,
                    issuer=issuer,
                    audience=audience,
                )
            except (jose.JWTError, ValueError):
                logger.error(
                    "Internal service token validation failed for issuer=%s audience=%s",
                    issuer,
                    audience,
                )

        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal service token",
        )

    return wrap
