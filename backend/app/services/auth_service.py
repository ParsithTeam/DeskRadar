from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenCreateData


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def authenticate(self, email: str, password: str) -> dict | None:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        if user.get("disabled"):
            return None
        return user

    async def login(self, email: str, password: str) -> dict | None:
        user = await self.authenticate(email, password)
        if not user:
            return None
        token_data = TokenCreateData(user_id= user["user_id"], role=user["role"])
        token = create_access_token(data=token_data)
        return {"access_token": token, "token_type": "bearer"}
