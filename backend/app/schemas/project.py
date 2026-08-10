from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from ..enums import Status
from datetime import datetime
from ..schemas.user import UserBriefResponse


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100, description='Название проекта')
    description: Optional[str] = Field(None, max_length=2000, description='Описание проекта (не более 2000 символов)')
    status: Status = Field(..., description='Статус проекта')


class ProjectCreate(ProjectBase):
    member_ids: Optional[List[int]] = Field(default=[], description='Id участников проекта')

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[Status] = None

class ProjectResponse(ProjectBase):
    id: int = Field(..., description='id проекта')
    owner_id: int = Field(..., gt=0, description='id владельца проекта')
    members: Optional[List[UserBriefResponse]] = []
    created_at: datetime = Field(..., description='Время создания')
    updated_at: datetime = Field(..., description='Время обновления')

    model_config = ConfigDict(from_attributes=True)

class UpdateMembersRequest(BaseModel):
    member_ids: List[int] = Field(..., descritption='Список id членов проекта')