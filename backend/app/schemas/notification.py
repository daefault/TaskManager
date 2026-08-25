from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from ..enums import NotificationType
from datetime import datetime



class NotificationBase(BaseModel):
    user_id: int = Field(..., gt=0, description='id пользователя')
    notification_type: NotificationType = Field(..., description='Тип уведомления')
    message: str = Field(..., max_length=1000, description='Сообщение пользователю (не более 1000 символов)')
    link: Optional[str] = Field(None, max_length=500, description='Ссылка на задачу')
    is_read: bool = False
    
class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: int = Field(..., description='id уведомления')
    created_at: datetime = Field(..., description='Время создания уведомления')
    updated_at: datetime = Field(..., description='Время обновления уведомления')
    link: Optional[str] = Field(None, description='Ссылка на задачу')
    
    model_config = ConfigDict(from_attributes=True)

#Модель для множественного удаления и отметок о прочитанности уведомления
class BulkActionRequest(BaseModel):
    notification_ids: List[int]