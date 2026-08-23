from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from ..schemas.user import UserBriefResponse


class CommentBase(BaseModel):
    content: str = Field(..., max_length=2000, description='Текст комментария (не более 2000 символов)')
    task_id: int = Field(..., gt=0, description='id задачи')


    
class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=2000)

    
class CommentResponse(CommentBase):
    id: int = Field(..., description='id комментария')
    author_id: int = Field(..., gt=0, description='id автора комментария')
    created_at: datetime = Field(..., description='Время создания')
    updated_at: datetime = Field(..., description='Время обновления')
    author: Optional[UserBriefResponse] = None

    model_config = ConfigDict(from_attributes=True)
