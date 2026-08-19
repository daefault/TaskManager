from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Tuple
from datetime import datetime, timedelta

from app.models import User
from app.repositories import UserRepository
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, TokenRefresh
from app.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserCreate
from app.repositories import UserRepository
from app.services import UserService


class AuthService:
    def __init__(self, user_repository: UserRepository, user_service: UserService):
        self.user_repository = user_repository
        self.user_service = user_service

    def register_user(self, user_data: UserRegister) -> Tuple[User, TokenResponse]:
        hashed_password = hash_password(user_data.password)
        user_create_data = UserCreate(
            username=user_data.username, 
            email=user_data.email,
            password=hashed_password
        )
        user = self.user_service.create_user(user_create_data)
        self.user_repository.update_user_activity(user.id)
        return self._create_tokens_for_user(user)

    def login_user(self, login_data: UserLogin) -> TokenResponse:
        user = self.user_repository.get_by_username(login_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неверное имя пользователя или пароль',
                headers={'WWW-Authenticate': 'Bearer'})

        if not user.is_active:
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail='Учётная запись отключена'
            ) 
        
        if not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неверное имя пользователя или пароль',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        self.user_repository.update_user_activity(user.id)
        return self._create_tokens_for_user(user)

    def refresh_access_token(self, refresh_data: TokenRefresh) -> TokenResponse:
        payload = decode_token(refresh_data.refresh_token)
        if not payload: 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Невалидный refresh токен',
                headers={'WWW-Authenticate': 'Bearer'}
            )
        if payload.get('type') != 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный тип токена",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = payload.get('sub')
        if not user_id: 
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный payload токена",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = self.user_repository.get_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self._create_tokens_for_user(user)

    def _create_tokens_for_user(self, user) -> TokenResponse:
        token_data = {
            'sub': str(user.id),
            'username': user.username,
            'email': user.email}
        return TokenResponse(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data)
        )