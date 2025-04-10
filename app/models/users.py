from pydantic import BaseModel


class User(BaseModel):
    email: str


class UserIn(User):
    password: str
