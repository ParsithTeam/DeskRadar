from datetime import datetime

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

    def extract_user_date(self):
        return {
            "requester": self.sub, #requester = user id
            "role": self.role,
            "name": self.name,
            "department": self.dept,
        }

class TokenCreateData(BaseModel):
    """
    اسکیما داده های لازم برای ساخت توکن جدید
    """
    user_id: int
    role: Role
    name: str = Field(max_length=50)
    department: str | None = Field(max_length=25)

    # متد ساخت پیلود برای استفاده در security
    def build_payload(self, exp: datetime):
        return {
            "sub": str(self.user_id),
            "role": self.role,
            "name": self.name,
            "dept": self.department,
            "exp": exp,
        }


class LoginRequest(BaseModel):
    email: str
    password: str