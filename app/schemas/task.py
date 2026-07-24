from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List
from ..enums import TaskStatus, Priority
from datetime import datetime, timezone
from .user import UserBriefResponse

class TaskBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200, description='Название задачи')
    description: Optional[str] = Field(None, max_length=2000, descripton='Описание задачи (не более 2000 символов)')
    status: TaskStatus = Field(TaskStatus.PENDING, description='Статус задачи')
    priority: Priority = Field(Priority.LOW, description='Приоритет задачи')
    deadline: Optional[datetime] = Field(None, description='Дедлайн задачи')
    project_id: int = Field(..., gt=0, description='id проекта')
    creator_id: int = Field(..., gt=0, description='id создателя задачи')
    
class TaskCreate(TaskBase):
    assignee_ids: Optional[List[int]] = Field(default=[], description='ID исполнителей')

    @field_validator('deadline')
    @classmethod
    def validate_deadline(cls, v: Optional[datetime]) -> Optional[datetime]: #проверка что дедлайн не в прошлом
        if v is None:
            return v
        now = datetime.now(timezone.utc)
        if v < now:
            raise ValueError('Дедлайн не может быть в прошлом')
        return v
    
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    deadline: Optional[datetime] = None
    project_id: Optional[int] = Field(None, gt=0)
    creator_id: Optional[int] = Field(None, gt=0)
    assignee_ids: Optional[List[int]] = Field(None)

    @field_validator('deadline')
    @classmethod
    def validate_deadline_update(cls, v: Optional[datetime], info) -> Optional[datetime]:
        if v is not None:
            return v
        now = datetime.now(timezone.utc)
        if v < now:
            status = info.data.get('status')
            if status in [TaskStatus.DONE, TaskStatus.CANCELLED]:
                return v
            raise ValueError('Нельзя установить дедлайн на прошедшую дату')
        return v

class TaskResponse(TaskBase):
    id: int = Field(..., description='id задачи')
    created_at: datetime = Field(..., description='Время создания')
    updated_at: datetime = Field(..., description='Время обновления')
    assignees: Optional[List['UserBriefResponse']] = []
    
    model_config = ConfigDict(from_attributes=True)
