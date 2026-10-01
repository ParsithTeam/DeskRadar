from pydantic import BaseModel, field_validator, Field

from app.schemas.user import Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int
    role: Role
    name: str = Field(max_length=50)
    dept: str | None = Field(max_length=25)
    exp: int
    @field_validator("sub", mode="before")
    @classmethod
    def parse_sub(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("sub must be a numeric string")
        return v

class TokenCreateData(BaseModel):
    """
    اسکیما داده های لازم برای ساخت توکن جدید
    """
    user_id: int
    role: Role
    name: str = Field(max_length=50)
    department: str | None = Field(max_length=25)


class LoginRequest(BaseModel):
    email: str
    password: str