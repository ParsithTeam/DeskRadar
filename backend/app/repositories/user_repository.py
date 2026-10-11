from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import Role


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self) -> None:
            await self.session.commit()

    def _to_dict(self, user: User) -> dict:
        role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
        return {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "hashed_password": user.hashed_password,
            "department": user.department,
            "role": role_val,
            "disabled": user.disabled,
        }

    async def get_by_email(self, email: str) -> dict | None:

        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return self._to_dict(user)

    async def get_by_id(self, user_id: int) -> dict | None:

        stmt = select(User).where(User.user_id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            return None

        return self._to_dict(user)

    async def create(
        self,
        email: str,
        name: str,
        hashed_password: str,
        role: Role = Role.USER,
        department: str | None = None,
        disabled: bool = False,
    ) -> dict:
        if self.session is None:
            raise RuntimeError("Database session is not available.")

        user = User(
            email=email,
            name=name,
            hashed_password=hashed_password,
            role=role,
            department=department,
            disabled=disabled,
        )
        self.session.add(user)
        await self.session.flush()
        return self._to_dict(user)

    async def get_all(self, offset: int = 0, limit: int = 100) -> list[dict]:

        stmt = select(User).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        users = result.scalars().all()
        return [self._to_dict(u) for u in users]