from datetime import datetime
from typing import Optional
from pydantic import ConfigDict
from app.schemas.common import BaseResponse

class UserResponse(BaseResponse):
    id: int
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=False)  # Important: set to False