from sqlalchemy.orm import Session
from typing import List
from ..repositories import UserRepository
from ..schemas.user import UserResponse, UserCreate, UserUpdate, UserBriefResponse
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.repository = user_repository

    def get_all_users(self) -> List[UserBriefResponse]:
        users = self.repository.get_all()
        return [UserBriefResponse.model_validate(user) for user in users]

    def get_user_by_id(self, user_id: int) -> UserResponse:
        user = self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        return UserResponse.model_validate(user)

    def create_user(self, user_data: UserCreate) -> UserResponse:
        if self.repository.get_by_username(user_data.username):
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Имя {user_data.username} уже занято'
                )
        if self.repository.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Email "{user_data.email}" уже используется'
            )
        user = self.repository.create(user_data)
        return UserResponse.model_validate(user)

    # def get_multiple_user_by_id(self, user_ids: List[int]) -> List[UserBriefResponse]:
    #     users = self.repository.get_multiple_by_ids(user_ids)
    #     if not users:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail="Пользователи с такими id не найдены"
    #         )
    #     return [UserBriefResponse.model_validate(user) for user in users]

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        if not self.repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )

        if user_data.username:
            existing = self.repository.get_by_username(user_data.username)
            if existing and existing.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Имя {user_data.username} уже занято'
                )
        if user_data.email:
            existing = self.repository.get_by_email(user_data.email)
            if existing and existing.id !=user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'email {user_data.email} уже занят'
                )
        updated_user = self.repository.update(user_id, user_data)
        return UserResponse.model_validate(updated_user)

    def delete_user(self, user_id: int) -> None:
        if not self.repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        self.repository.soft_delete(user_id)
        logger.info('User %s deleted successfully', user_id)
        from app.tasks import send_user_inactive_reminder
        send_user_inactive_reminder.delay(user_id)


    def get_by_username(self, username: str) -> UserResponse:
        user = self.repository.get_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с username {username} не найден'
            )
        return UserResponse.model_validate(user)

    def get_by_email(self, email: str) -> UserResponse:
        user = self.repository.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с email {email} не найден'
            )
        return UserResponse.model_validate(user)

    def restore_user(self, user_id: int) -> UserResponse:
        user = self.repository.restore_user(user_id)
        if not user: 
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail='Пользователь не найден'
            )
        logger.info('User %s restored successfully', user_id)
        return UserResponse.model_validate(user)

    def search_users(self, query: str, limit: int = 10) -> List[UserResponse]:
        users = self.repository.search_users(query, limit)
        return [UserResponse.model_validate(user) for user in users]