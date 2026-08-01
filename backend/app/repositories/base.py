from sqlalchemy.orm import Session
from typing import List, Optional, Generic, TypeVar, Type
from pydantic import BaseModel

UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
class BaseRepository(Generic[ModelType]):
    
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def create(self, data: CreateSchemaType) -> ModelType:
        db_data = self.model(**data.model_dump())
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return db_data

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multiple_by_ids(self, ids: List[int]) -> List[ModelType]:
        return(
            self.db.query(self.model)
            .filter(self.model.id.in_(ids))
            .all()
        )
        
    def get_all(self, skip: int = 0, limit: int = 100, filters: Optional[dict] = None) -> List[ModelType]:
        query = self.db.query(self.model)
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        query = query.offset(skip).limit(limit)
        return query.all()

    def update(self, id: int, data: UpdateSchemaType) -> Optional[ModelType]:
        if not self.exists(id):
            return
        to_update = self.db.query(self.model).filter(self.model.id == id).first()
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(to_update, key):
                setattr(to_update, key, value)
        self.db.commit()
        self.db.refresh(to_update)

        return to_update


    def delete(self, id: int) -> bool:
        to_delete = self.db.query(self.model).filter(self.model.id == id).first()
        if not to_delete:
            return False
        self.db.delete(to_delete)
        self.db.commit()
        return True

    def exists(self, id: int) -> bool:
        find_data = self.db.query(self.model).filter(self.model.id == id).first()
        if not find_data:
            return False
        return True
