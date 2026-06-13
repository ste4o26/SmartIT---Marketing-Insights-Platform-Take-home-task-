import pydantic

class SigninRequest(pydantic.BaseModel):

    username: str
    password: str