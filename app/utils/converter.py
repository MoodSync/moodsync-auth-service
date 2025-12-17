from datetime import datetime
from typing import Any, Dict
from app.schemas.response.user import UserResponse
from app.database.models import User

def user_to_response(user: User) -> UserResponse:
    """Convert SQLAlchemy User model to UserResponse schema."""
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )

def model_to_dict(model: Any, exclude: list = None) -> Dict:
    """Generic model to dict converter."""
    if exclude is None:
        exclude = []
    
    result = {}
    for column in model.__table__.columns:
        if column.name in exclude:
            continue
        value = getattr(model, column.name)
        if isinstance(value, datetime):
            value = value.isoformat()
        result[column.name] = value
    return result