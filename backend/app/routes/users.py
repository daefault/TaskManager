from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import List
from ..dependencies import get_user_service, require_admin, get_current_user, get_notification_service
from ..services import UserService, NotificationService
from ..schemas.user import UserResponse, UserBriefResponse, UserCreate, UserUpdate
from ..models import User


router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.get('', response_model=List[UserBriefResponse], status_code=status.HTTP_200_OK)
def get_all_users(service: UserService = Depends(get_user_service), admin: User = Depends(require_admin)):
    return service.get_all_users()

@router.post('', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, service: UserService = Depends(get_user_service), admin: User = Depends(require_admin)):
    return service.create_user(user_data)

@router.get('/by-username/', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_by_username(
    username: str = Query(..., min_length=1, max_length=50, description='Имя пользователя'),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
    ):
    user = service.get_by_username(username)
    if user.id != current_user.id and not current_user.is_admin:
       raise HTTPException(
                   status_code=status.HTTP_403_FORBIDDEN,
                   detail='Недостаточно прав для выполнения операции'
               )
    return user

@router.get('/search', response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def search_users(
    query: str = Query(..., min_length=1, max_length=100, description='Поисковый запрос'),
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
):
    return service.search_users(query)

@router.get('/by-email/', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_by_email(
    email: str = Query(..., max_length=100, description='Email пользователя'), 
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user)
    ):
    user = service.get_by_email(email)
    if user.id !=current_user.id and not current_user.is_admin:
        raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Недостаточно прав для выполнения операции'
                )
    return user

@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, service: UserService = Depends(get_user_service), current_user: User = Depends(get_current_user)):
    user = service.get_user_by_id(user_id)
    if current_user.id != user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    return user

@router.put('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_data: UserUpdate, service: UserService = Depends(get_user_service), admin: User = Depends(require_admin)):
    return service.update_user(user_id, user_data)

@router.patch('/{user_id}', status_code=status.HTTP_200_OK)
def restore_user(user_id: int, service: UserService = Depends(get_user_service), admin: User = Depends(require_admin)):
    return service.restore_user(user_id)
     
@router.patch('/soft-delete/{user_id}', status_code=status.HTTP_200_OK)
def delete_user(
    user_id: int, 
    service: UserService = Depends(get_user_service), 
    notification_service: NotificationService = Depends(get_notification_service),  
    admin: User = Depends(require_admin)
    ):
    service.delete_user(user_id)
    notification_service.user_inactive_reminder(user_id)