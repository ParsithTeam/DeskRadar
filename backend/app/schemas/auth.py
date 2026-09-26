from pydantic import BaseModel, field_validator

from app.schemas.user import Role


class Token(BaseModel):
    acs_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: int
    role: Role
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

class LoginRequest(BaseModel):
    email: str
    password: str