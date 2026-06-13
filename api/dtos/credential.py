import pydantic


class Credential(pydantic.BaseModel):

    username: str
    password: str
