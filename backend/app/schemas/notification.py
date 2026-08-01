from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from ..enums import NotificationType
from datetime import datetime


class NotificationBase(BaseModel):
    user_id: int = Field(..., gt=0, description='id пользователя')
    notification_type: NotificationType = Field(..., description='Тип уведомления')
    message: str = Field(..., max_length=1000, description='Сообщение пользователю (не более 1000 символов)')
    is_read: bool = False
    
class NotificationCreate(NotificationBase):
    pass

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationResponse(NotificationBase):
    id: int = Field(..., description='id уведомления')
    created_at: datetime = Field(..., description='Время создания уведомления')
    updated_at: datetime = Field(..., description='Время обновления уведомления')
    
    model_config = ConfigDict(from_attributes=True)
