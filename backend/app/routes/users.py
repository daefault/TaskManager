from fastapi import APIRouter, Depends, status, Query
from typing import List
from ..dependencies import get_user_service, require_admin
from ..services import UserService
from ..schemas.user import UserResponse, UserBriefResponse, UserCreate, UserUpdate
from ..models import User

router = APIRouter(
    prefix='/users',
    tags=['users']
)

@router.get('', response_model=List[UserBriefResponse], status_code=status.HTTP_200_OK)
def get_all_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()

@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, service: UserService = Depends(get_user_service)):
    return service.get_user_by_id(user_id)

@router.get('/by-username/', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_by_username(
    username: str = Query(..., min_length=1, max_length=50, description='Имя пользователя'),
    service: UserService = Depends(get_user_service)
    ):
    return service.get_by_username(username)

@router.get('/by-email/', response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_by_email(
    email: str = Query(..., max_length=100, description='Email пользователя'), 
    service: UserService = Depends(get_user_service)):
    return service.get_by_email(email)

@router.post('', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, service: UserService = Depends(get_user_service), admin: User = Depends(require_admin)):
    return service.create_user(user_data)

@router.put('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_data: UserUpdate, service: UserService = Depends(get_user_service)):
    return service.update_user(user_id, user_data)

@router.delete('/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)):
    service.delete_user(user_id)

     
