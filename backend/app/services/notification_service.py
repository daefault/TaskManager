from sqlalchemy.orm import Session
from typing import List, Optional
from ..repositories import NotificationRepository, UserRepository
from ..schemas.notification import NotificationResponse, NotificationCreate, NotificationUpdate
from fastapi import HTTPException, status
from ..enums import NotificationType
from ..config import settings
from ..models import Notification


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
        if self.repository.get_by_user_count(notification_data.user_id) >= settings.MAX_NOTIFICATIONS_PER_USER:
            self.repository.delete_old_notification_for_user(notification_data.user_id, days=settings.DAYS_TO_DELETE_NOTIFICATIONS)
        notification = self.repository.create(notification_data)
        return NotificationResponse.model_validate(notification)

    # def update_notification(self, notification_id: int, notification_data: NotificationUpdate) -> NotificationResponse:
    #     if not self.repository.exists(notification_id):
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=f'Уведомление с id {notification_id} не найдено'
    #         )
    #     updated_notification = self.repository.update(notification_id, notification_data)
    #     return NotificationResponse.model_validate(updated_notification)

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
            is_read: Optional[bool] = None
) -> tuple[List[Notification], int]:
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        notifications = self.repository.get_by_user(user_id, skip, limit, is_read)
        total = self.repository.get_by_user_count(user_id, is_read)
        return notifications, total

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

    def bulk_mark_as_read(self, user_id: int, notification_ids: List[int]) -> int:
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь {user_id} не найден'
            )
        for notification in notification_ids:
            if not self.repository.exists(notification):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Уведомление не найдено'
                ) 
        count = self.repository.bulk_mark_as_read(user_id, notification_ids)
        return count

    def bulk_delete(self, user_id: int, notification_ids: List[int]) -> int:
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь {user_id} не найден'
            ) 
        for notification in notification_ids:
            if not self.repository.exists(notification):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Уведомление не найдено'
                ) 
        count = self.repository.bulk_delete(user_id, notification_ids)
        return count

    def delete_all_read(self, user_id: int) -> int:
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь {user_id} не найден'
            ) 
        count = self.repository.delete_all_read(user_id)
        return count


#МЕТОДЫ ДЛЯ СОЗДАНИЯ РАЗНЫХ ТИПОВ УВЕДОМЛЕНИЙ
    def notify_task_assigned(self, user_id: int, task_title: str, task_id: int) -> NotificationResponse:
        message = f'Вам назначена задача: {task_title}'
        link = f'/tasks/{task_id}'
        notification = NotificationCreate(user_id=user_id, notification_type=NotificationType.TASK_ASSIGNED, message=message, link=link)
        return self.create_notification(notification)

    def user_inactive_reminder(self, user_id: int) -> NotificationResponse:
        message = f'Ваша учётная запись была отключена из-за неактивности'
        notification = NotificationCreate(user_id=user_id, notification_type=NotificationType.USER_INACTIVE, message=message)
        if not self.user_repository.is_user_inactive(user_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Пользователь активен или не существует')
        if self.repository.get_by_user_count(notification.user_id) >= settings.MAX_NOTIFICATIONS_PER_USER:
            self.repository.delete_old_notification_for_user(notification.user_id, days=settings.DAYS_TO_DELETE_NOTIFICATIONS)
        notification = self.repository.create(notification)
        return NotificationResponse.model_validate(notification)