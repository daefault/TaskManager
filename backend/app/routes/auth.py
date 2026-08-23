from fastapi import APIRouter, Depends, status, Query, HTTPException
from ..dependencies import get_auth_service, get_current_user
from ..models import User
from ..schemas.auth import UserRegister, UserLogin, TokenResponse, TokenRefresh, UserOut
from ..services import AuthService


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

@router.post('/register', response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.register_user(user_data)

@router.post('/login', response_model=TokenResponse)
def login(login_data: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login_user(login_data)

@router.post('/refresh', response_model=TokenResponse)
def refresh(refresh_data: TokenRefresh, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.refresh_access_token(refresh_data)

@router.get('/me', response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post('/logout')
def logout():
    return {'message': 'Успешный выход'}