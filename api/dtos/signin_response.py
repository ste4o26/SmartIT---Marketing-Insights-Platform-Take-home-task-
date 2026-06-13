import pydantic


class SigninResponse(pydantic.BaseModel):

    access_token: str | None
    expires_in: int | None
    token_type: str | None
