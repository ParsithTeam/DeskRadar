from enum import Enum

from pydantic import BaseModel

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(BaseModel):
    user_id: int
    email: str
    department: str | None
    full_name: str
    role:  Role      # user | admin
    disabled: bool = False