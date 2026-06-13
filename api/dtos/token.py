import pydantic


class Token(pydantic.BaseModel):

    access_token: str | None
    expires_in: int | None
    refresh_token: str | None
    refresh_expires_in: int | None
    token_type: str | None
