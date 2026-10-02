from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password


# in-memory DB موقت
FAKE_USERS_DB: dict[str, dict] = {
    "hossein@gmail.com": {
        "user_id": 777,
        "name": "Hossein",
        "department": "Front",
        "email": "hossein@gmail.com",
        "role": "admin",
        "disabled": False,
        "hashed_password": hash_password("admin123"),
    },
    "danial@gmail.com": {
        "user_id": 700,
        "name": "Danial",
        "department": "Backend",
        "email": "danial@gmail.com",
        "role": "user",
        "disabled": False,
        "hashed_password": hash_password("ali123"),
    },
}


class UserRepository:
    def __init__(self, session: AsyncSession | None):
        self.session = session

    async def get_by_email(self, email: str) -> dict | None:
        return FAKE_USERS_DB.get(email)