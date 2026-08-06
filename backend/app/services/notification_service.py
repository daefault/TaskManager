from sqlalchemy.orm import Session
from typing import List, Optional
from ..repositories import NotificationRepository, UserRepository
from ..schemas.notification import NotificationResponse, NotificationCreate, NotificationUpdate
from fastapi import HTTPException, status
from ..enums import NotificationType


class NotificationService:
    def __init__(
            self,
            notification_repository: NotificationRepository,
            user_repository: UserRepository):
        self.repository = notification_repository
        self.user_repository = user_repository

    def get_all_notification(self) -> List[NotificationResponse]:
        notifications = self.repository.get_all()
        return [NotificationResponse.model_validate(notification) for notification in notifications]

    def get_notification_by_id(self, notification_id: int) -> NotificationResponse:
        notification = self.repository.get_by_id(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Уведомление с id {notification_id} не найдено'
            )
        return NotificationResponse.model_validate(notification)

    def create_notification(self, notification_data: NotificationCreate) -> NotificationResponse:
        if not self.user_repository.exists(notification_data.user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {notification_data.user_id} не найден'
            )
        notification = self.repository.create(notification_data)
        return NotificationResponse.model_validate(notification)

    def update_notification(self, notification_id: int, notification_data: NotificationUpdate) -> NotificationResponse:
        if not self.repository.exists(notification_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Уведомление с id {notification_id} не найдено'
            )
        updated_notification = self.repository.update(notification_id, notification_data)
        return NotificationResponse.model_validate(updated_notification)

    def delete_notification(self, notification_id: int) -> None:
        if self.repository.delete(notification_id):
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Уведомление с id {notification_id} не найдено'
            )

    def get_user_notifications(
            self, 
            user_id: int, 
            skip: int = 0, 
            limit: int = 100, 
            is_read: Optional[bool] = False
) -> List[NotificationResponse]:
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        notifications = self.repository.get_by_user(user_id, skip, limit, is_read)
        return [NotificationResponse.model_validate(n) for n in notifications]

    def get_unread_count(self, user_id: int) -> dict:
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        count = self.repository.get_by_user_count(user_id, is_read=False)
        return {'user_id': user_id, 'unread_count': count}

    def mark_as_read(self, notification_id: int) -> NotificationResponse:
        notification = self.repository.mark_as_read(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Уведомление с id {notification_id} не найдено'
            )
        return NotificationResponse.model_validate(notification)

    def mark_all_as_read(self, user_id: int) -> dict: 
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        count = self.repository.mark_all_as_read(user_id)
        return {'user_id': user_id, 'marked_count': count}

    def delete_old_notifications(self, days: int = 30) -> dict:
        count = self.repository.delete_old_notification(days)
        return {'deleted_count': count, 'older_than_days': days}

#МЕТОДЫ ДЛЯ СОЗДАНИЯ РАЗНЫХ ТИПОВ УВЕДОМЛЕНИЙ
    def notify_task_assigned(self, user_id: int, task_title: str) -> NotificationResponse:
        message = f'Вам назначена задача: {task_title}'
        notification = NotificationCreate(user_id=user_id, notification_type=NotificationType.TASK_ASSIGNED, message=message)
        return self.create_notification(notification)
        
    def notify_status_changed(self, user_id: int, task_title: str, new_status: str) -> NotificationResponse:
        message = f'Статус задачи {task_title} изменен на {new_status}'
        notification = NotificationCreate(user_id=user_id, notification_type=NotificationType.STATUS_CHANGED, message=message)
        return self.create_notification(notification)

    def notify_deadline_reminder(self, user_id: int, task_title: str, deadline: str) -> NotificationResponse:
        message = f'Приближается дедлайн задачи: {task_title} (до {deadline})'
        notification = NotificationCreate(user_id=user_id, notification_type=NotificationType.DEADLINE_REMINDER, message=message)
        return self.create_notification(notification)