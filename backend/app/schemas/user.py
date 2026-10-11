from enum import Enum

from pydantic import BaseModel

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class UserInfo(BaseModel):

    email: str
    department: str | None
    name: str
    role:  Role      # user | admin