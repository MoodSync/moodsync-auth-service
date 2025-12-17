from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.database.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
    
    async def get(self, id: int) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()
    
    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict] = None
    ) -> List[ModelType]:
        query = select(self.model)
        
        if filters:
            for field, value in filters.items():
                query = query.where(getattr(self.model, field) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        # Correct SQLAlchemy 2.0 syntax
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
        )
        await self.session.commit()
        return await self.get(id)
    
    async def delete(self, id: int) -> bool:
        # Correct SQLAlchemy 2.0 syntax
        await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return True
    
    async def exists(self, field: str, value: Any) -> bool:
        result = await self.session.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none() is not None