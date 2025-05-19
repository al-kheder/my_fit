from pydantic import BaseModel,EmailStr,Field


class User(BaseModel):
    email:EmailStr = Field(...,json_schema_extra={"example": "exampl@email.com"})


class UserIn(User):
    password: str
