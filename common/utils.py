import functools
import inspect
import typing

import httpx

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
            async with httpx.AsyncClient(base_url=base_url, timeout=timeout) as session:
                if is_method:
                    self_or_cls, *rest = args
                    return await fn(self_or_cls, session, *rest, **kwargs)
                return await fn(session, *args, **kwargs)

        return _wrap

    if func is not None:
        return _decorator(func)

    return _decorator
