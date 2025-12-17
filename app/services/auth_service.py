from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import security_manager
from app.repositories.user_repository import UserRepository
from app.repositories.otp_repository import OTPRepository
from app.services.otp_service import OTPService
from app.schemas.request.auth import RegisterRequest, LoginRequest
from app.schemas.response.auth import LoginResponse, RegisterResponse
from app.utils.validators import validate_password_strength
from app.utils.converter import user_to_response

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.otp_repo = OTPRepository(db)
        self.otp_service = OTPService(db)
    
    async def register(self, request: RegisterRequest) -> RegisterResponse:
        # Check if user exists
        if await self.user_repo.exists("email", request.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if request.phone and await self.user_repo.exists("phone", request.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Validate password
        validate_password_strength(request.password)
        
        # Create user
        user_data = {
            "email": request.email,
            "phone": request.phone,
            "hashed_password": security_manager.get_password_hash(request.password),
            "full_name": request.full_name,
            "is_active": False,
            "is_verified": False
        }
        
        user = await self.user_repo.create_user(user_data)
        
        # Send OTP for verification
        await self.otp_service.send_otp(
            user_id=user.id,
            email=user.email,
            phone=user.phone,
            purpose="registration"
        )
        
        return RegisterResponse(
            user=user,
            message="Registration successful. Please verify your email/phone with OTP."
        )
    
    async def login(self, request: LoginRequest) -> LoginResponse:
        user = await self.user_repo.get_by_email(request.email)
        
        if not user or not security_manager.verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your account first"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Create tokens
        access_token = security_manager.create_access_token({"sub": user.email})
        refresh_token = security_manager.create_refresh_token({"sub": user.email})
        
        user_response = user_to_response(user)
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response  # Fixed!
        )
    
    # async def verify_otp(self, email: str, otp_code: str, purpose: str):
    #     user = await self.user_repo.get_by_email(email)
    #     if not user:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="User not found"
    #         )
        
    #     is_valid = await self.otp_service.verify_otp(
    #         user_id=user.id,
    #         otp_code=otp_code,
    #         purpose=purpose
    #     )
        
    #     if not is_valid:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Invalid or expired OTP"
    #         )
        
    #     if purpose == "registration":
    #         await self.user_repo.verify_user(email)
        
    #     return {"message": "OTP verified successfully", "user": user}
    
    async def verify_otp(self, email: str, otp_code: str, purpose: str):
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        is_valid = await self.otp_service.verify_otp(
            user_id=user.id,
            otp_code=otp_code,
            purpose=purpose
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        if purpose == "registration":
            user = await self.user_repo.verify_user(email)
        
        # Convert SQLAlchemy User to UserResponse
        from app.schemas.response.user import UserResponse
        
        # Create UserResponse from the user object
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        
        return {"message": "OTP verified successfully", "user": user_response}
    
    async def refresh_token(self, refresh_token: str) -> dict:
        payload = security_manager.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        email = payload.get("sub")
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        new_access_token = security_manager.create_access_token({"sub": user.email})
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }