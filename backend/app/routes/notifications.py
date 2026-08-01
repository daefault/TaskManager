from fastapi import APIRouter, Depends, status, Query
from typing import List
from ..dependencies import get_notification_service
from ..services import NotificationService
from ..schemas.notification import NotificationResponse, NotificationCreate, NotificationUpdate

router = APIRouter(
    prefix='/notificatons',
    tags=['notifications']
)

@router.get('', response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
def get_all_notifications(service: NotificationService = Depends(get_notification_service)):
    return service.get_all_notification()

@router.get('/{notification_id}', response_model=NotificationResponse, status_code=status.HTTP_200_OK)
def get_notification_by_id(notification_id: int, service: NotificationService = Depends(get_notification_service)):
    return service.get_notification_by_id(notification_id)

@router.post('', response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(notification_data: NotificationCreate, service: NotificationService = Depends(get_notification_service)):
    return service.create_notification(notification_data)

@router.put('/{notification_id}', response_model=NotificationResponse, status_code=status.HTTP_200_OK)
def update_notification(notification_id: int, notification_data: NotificationUpdate, service: NotificationService = Depends(get_notification_service)):
    return service.update_notification(notification_id, notification_data)

@router.delete('/{notification_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, service: NotificationService = Depends(get_notification_service)):
    return service.delete_notification(notification_id)
