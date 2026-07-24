from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from ..enums import Status
from datetime import datetime


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100, description='Название проекта')
    description: Optional[str] = Field(None, max_length=2000, descripton='Описание проекта (не более 2000 символов)')
    status: Status = Field(..., description='Статус проекта')
    owner_id: int = Field(..., gt=0, description='id владельца проекта')

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[Status] = None
    owner_id: Optional[int] = Field(None, gt=0)

class ProjectResponse(ProjectBase):
    id: int = Field(..., description='id проекта')
    created_at: datetime = Field(..., description='Время создания')
    updated_at: datetime = Field(..., description='Время обновления')

    model_config = ConfigDict(from_attributes=True)
