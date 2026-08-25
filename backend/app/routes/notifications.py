from fastapi import APIRouter, Depends, status, Query, HTTPException, status
from typing import List, Optional
from ..dependencies import get_notification_service, get_current_user, require_admin
from ..services import NotificationService
from ..schemas.notification import NotificationResponse, NotificationCreate, NotificationUpdate, BulkActionRequest
from ..models import User


router = APIRouter(
    prefix='/notifications',
    tags=['notifications']
)

@router.get('/all', response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
def get_all_notifications(
    service: NotificationService = Depends(get_notification_service), 
    admin: User = Depends(require_admin)
):
    return service.get_all_notification()

@router.put('/read-all', response_model=dict)
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    return service.mark_all_as_read(current_user.id)

@router.get('/unread-count', response_model=dict, status_code=status.HTTP_200_OK)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    return service.get_unread_count(current_user.id)

@router.put('/bulk-read', response_model=dict, status_code=status.HTTP_200_OK)
def bulk_mark_as_read(
    request: BulkActionRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    count = service.bulk_mark_as_read(current_user.id, request.notification_ids)
    return {'marked_count': count}

@router.delete('/bulk-delete', response_model=dict, status_code=status.HTTP_200_OK)
def bulk_delete(
    request: BulkActionRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    count = service.bulk_delete(current_user.id, request.notification_ids)
    return {'deleted_count': count}

@router.delete('/delete-read', response_model=dict, status_code=status.HTTP_200_OK)
def delete_read_notifications(
    current_user: User = Depends(get_current_user), 
    service: NotificationService = Depends(get_notification_service)
):
    count = service.delete_all_read(current_user.id)
    return {'deleted_count': count}
# @router.post('', response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
# def create_notification(
#     notification_data: NotificationCreate, 
#     service: NotificationService = Depends(get_notification_service),
#     admin: User = Depends(require_admin)    
#     ):
#     return service.create_notification(notification_data)

@router.get('', response_model=dict, status_code=status.HTTP_200_OK)
def get_my_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, le=100),
    is_read: Optional[bool] = Query(None, description='Фильтр по прочитанности'),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service)
):
    notifications, total = service.get_user_notifications(current_user.id, skip, limit, is_read)
    return {
        'items': [NotificationResponse.model_validate(n) for n in notifications],
        'total': total,
        'skip': skip,
        'limit': limit
    }

# @router.get('/{notification_id}', response_model=NotificationResponse, status_code=status.HTTP_200_OK)
# def get_notification_by_id(
#     notification_id: int, 
#     service: NotificationService = Depends(get_notification_service),
#     admin: User = Depends(require_admin)
# ):
#     return service.get_notification_by_id(notification_id)

# @router.put('/{notification_id}', response_model=NotificationResponse, status_code=status.HTTP_200_OK)
# def update_notification(
#     notification_id: int, 
#     notification_data: NotificationUpdate, 
#     service: NotificationService = Depends(get_notification_service),
#     admin: User = Depends(require_admin)
# ):
#     return service.update_notification(notification_id, notification_data)

@router.delete('/{notification_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int, 
    service: NotificationService = Depends(get_notification_service),
    current_user: User = Depends(get_current_user)
):
    notification = service.get_notification_by_id(notification_id)
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Это уведомление не принадлежит вам')
    service.delete_notification(notification_id)

@router.put('/{notification_id}/read', response_model=NotificationResponse, status_code=status.HTTP_200_OK)
def mark_as_read(
    notification_id: int, 
    current_user: User = Depends(get_current_user), 
    service: NotificationService = Depends(get_notification_service)
):
    notification = service.get_notification_by_id(notification_id)
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Это не ваше уведомление')
    return service.mark_as_read(notification_id)