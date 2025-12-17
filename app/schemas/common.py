from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaginationParams(BaseModel):
    page: int = 1
    per_page: int = 10
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"page": 1, "per_page": 10}
        }
    )