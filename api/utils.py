import fastapi


def set_cookie(
    response: fastapi.Response, *, key: str, value: str, expires_in: int | None = None
) -> None:
    response.set_cookie(
        key=key,
        value=value,
        max_age=expires_in,
        httponly=True,
        secure=False,
        samesite="lax",
    )
