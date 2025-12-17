from datetime import datetime
from typing import Optional
from app.schemas.common import BaseResponse
from app.schemas.response.user import UserResponse

class TokenResponse(BaseResponse):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class LoginResponse(TokenResponse):
    user: UserResponse

class RegisterResponse(BaseResponse):
    user: UserResponse
    message: str = "OTP sent to your email/phone"

class OTPResponse(BaseResponse):
    message: str = "OTP sent successfully"
    otp_type: str
    expires_in: int  # minutes

class VerifyOTPResponse(BaseResponse):
    message: str = "OTP verified successfully"
    user: Optional[UserResponse] = None

class RefreshTokenResponse(TokenResponse):
    pass