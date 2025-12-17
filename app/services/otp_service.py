import random
import string
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.repositories.otp_repository import OTPRepository
from app.services.email_service import EmailService
from app.utils.otp import generate_otp

class OTPService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.otp_repo = OTPRepository(db)
        self.email_service = EmailService()
    
    async def send_otp(self, user_id: int, email: str, phone: Optional[str], purpose: str):
        # Invalidate previous OTPs
        await self.otp_repo.invalidate_user_otps(user_id, purpose)
        
        # Generate OTP
        otp_code = generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        # Create OTP record
        otp_data = {
            "user_id": user_id,
            "otp_code": otp_code,
            "otp_type": "email",  # Default to email
            "purpose": purpose,
            "expires_at": expires_at
        }
        
        await self.otp_repo.create_otp(otp_data)
        
        # Send OTP via email
        await self.email_service.send_otp_email(email, otp_code, purpose)
        
        # TODO: Implement SMS service for phone OTP
        
        return {"message": f"OTP sent to {email}"}
    
    async def verify_otp(self, user_id: int, otp_code: str, purpose: str) -> bool:
        otp = await self.otp_repo.get_valid_otp(user_id, otp_code, purpose)
        
        if otp:
            otp.is_used = True
            await self.db.commit()
            return True
        
        return False
    
    async def resend_otp(self, user_id: int, email: str, purpose: str):
        return await self.send_otp(user_id, email, None, purpose)