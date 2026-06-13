import pydantic


class Credential(pydantic.BaseModel):

    username: str | None = None
    password: str | None = None
    refresh_token: str | None = None

    @pydantic.model_validator(mode="after")
    def validate_credentials(self):
        if self.username and self.password and self.refresh_token:
            raise pydantic.ValidationError(
                "Provide either username and password, or refresh token"
            )

        if bool(self.username) != bool(self.password):
            raise ValueError("Username and password must be provided together")
        return self
