from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.database.models import OTP
from app.repositories.base_repository import BaseRepository

class OTPRepository(BaseRepository[OTP]):
    def __init__(self, session: AsyncSession):
        super().__init__(OTP, session)
    
    async def get_valid_otp(self, user_id: int, otp_code: str, purpose: str) -> Optional[OTP]:
        result = await self.session.execute(
            select(OTP).where(
                and_(
                    OTP.user_id == user_id,
                    OTP.otp_code == otp_code,
                    OTP.purpose == purpose,
                    OTP.is_used == False,
                    OTP.expires_at > datetime.utcnow()
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def invalidate_user_otps(self, user_id: int, purpose: str):
        # Correct SQLAlchemy 2.0 syntax for update
        await self.session.execute(
            update(OTP)
            .where(
                and_(
                    OTP.user_id == user_id,
                    OTP.purpose == purpose,
                    OTP.is_used == False
                )
            )
            .values(is_used=True)
        )
        await self.session.commit()
    
    async def create_otp(self, otp_data: dict) -> OTP:
        return await self.create(otp_data)