import pydantic


class Token(pydantic.BaseModel):

    access_token: str
    expires_in: int
    token_type: str
    refresh_token: str | None = pydantic.Field(default=None)
    refresh_expires_in: int | None = pydantic.Field(default=None)
