from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db 

from app.schemas.request.auth import (
    RegisterRequest, 
    LoginRequest, 
    OTPRequest,
    OTPVerifyRequest,
    RefreshTokenRequest,
    ResetPasswordRequest
)
from app.schemas.response.auth import (
    RegisterResponse,
    LoginResponse,
    OTPResponse,
    VerifyOTPResponse,
    RefreshTokenResponse
)
from app.services.auth_service import AuthService

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    return await auth_service.register(request)

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    return await auth_service.login(request)

@router.post("/request-otp", response_model=OTPResponse)
async def request_otp(
    request: OTPRequest,
    db: AsyncSession = Depends(get_db)
):
    from app.services.otp_service import OTPService
    from app.repositories.user_repository import UserRepository
    
    user_repo = UserRepository(db)
    otp_service = OTPService(db)
    
    user = await user_repo.get_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    result = await otp_service.send_otp(
        user_id=user.id,
        email=user.email,
        phone=user.phone,
        purpose=request.purpose
    )
    
    return OTPResponse(
        message=result["message"],
        otp_type=request.otp_type,
        expires_in=10  # minutes
    )

@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    result = await auth_service.verify_otp(
        email=request.email,
        otp_code=request.otp_code,
        purpose=request.purpose
    )
    
    return VerifyOTPResponse(
        message=result["message"],
        user=result["user"]
    )

@router.post("/refresh-token", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_token(request.refresh_token)
    
    return RefreshTokenResponse(**tokens)

@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    from app.services.auth_service import AuthService
    from app.repositories.user_repository import UserRepository
    from app.core.security import security_manager
    
    auth_service = AuthService(db)
    user_repo = UserRepository(db)
    
    # Verify OTP first
    await auth_service.verify_otp(
        email=request.email,
        otp_code=request.otp_code,
        purpose="reset_password"
    )
    
    # Update password
    user = await user_repo.get_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    hashed_password = security_manager.get_password_hash(request.new_password)
    await user_repo.update_user(user.id, {"hashed_password": hashed_password})
    
    return {"message": "Password reset successfully"}