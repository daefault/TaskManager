from sqlalchemy.orm import Session
from typing import List
from ..repositories import NotificationRepository, UserRepository
from ..schemas.notification import NotificationResponse, NotificationCreate, NotificationUpdate
from fastapi import HTTPException, status

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

    def get_multiple_notification_by_id(self, notification_ids: List[int]) -> List[NotificationResponse]:
        notifications = self.repository.get_multiple_by_ids(notification_ids)
        if not notifications:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Уведомления с такими id не найдены"
            )
        return [NotificationResponse.model_validate(notification) for notification in notifications]

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
