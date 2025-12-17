from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import User
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_by_field("email", email)
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        return await self.get_by_field("phone", phone)
    
    async def create_user(self, user_data: dict) -> User:
        return await self.create(user_data)
    
    async def update_user(self, user_id: int, update_data: dict) -> Optional[User]:
        return await self.update(user_id, update_data)
    
    async def verify_user(self, email: str) -> Optional[User]:
        user = await self.get_by_email(email)
        if user:
            user.is_verified = True
            user.is_active = True
            await self.session.commit()
        return user