from sqlalchemy.orm import Session
from typing import List
from ..schemas.comment import CommentResponse, CommentCreate, CommentUpdate
from ..repositories import CommentRepository, UserRepository, TaskRepository

from fastapi import HTTPException, status

class CommentService:
    def __init__(
            self, 
            comment_repository: CommentRepository, 
            user_repository: UserRepository, 
            task_repository: TaskRepository
            ):
        self.repository = comment_repository
        self.user_repository = user_repository
        self.task_repository = task_repository

    def get_all_comment(self) -> List[CommentResponse]:
        comments = self.repository.get_all()
        return [CommentResponse.model_validate(comment) for comment in comments]

    def get_comment_by_id(self, comment_id: int) -> CommentResponse:
        comment = self.repository.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Комментарий с id {comment_id} не найден'
            )
        return CommentResponse.model_validate(comment)

    def create_comment(self, comment_data: CommentCreate, author_id: int) -> CommentResponse:
        if not self.task_repository.exists(comment_data.task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {comment_data.task_id} не найдена'
            )
        comment = self.repository.create(comment_data, author_id)
        return CommentResponse.model_validate(comment)

    def get_multiple_comment_by_id(self, comment_ids: List[int]) -> List[CommentResponse]:
        comments = self.repository.get_multiple_by_ids(comment_ids)
        if not comments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Комментарии с такими id не найдены"
            )
        return [CommentResponse.model_validate(comment) for comment in comments]

    def update_comment(self, comment_id: int, comment_data: CommentUpdate) -> CommentResponse:
        if not self.repository.exists(comment_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Комментарий с id {comment_id} не найден'
            )
        updated_comment = self.repository.update(comment_id, comment_data)
        return CommentResponse.model_validate(updated_comment)

    def delete_comment(self, comment_id: int) -> None:
        if self.repository.delete(comment_id):
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Комментарий с id {comment_id} не найден'
            )

    def get_comments_by_task(self, task_id: int) -> List[CommentResponse]:
        if not self.task_repository.exists(task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найдена'
            )
        comments = self.repository.get_by_task_id(task_id)
        return [CommentResponse.model_validate(comment) for comment in comments]

    def get_comments_by_author(self, author_id: int) -> List[CommentResponse]:
        if not self.user_repository.exists(author_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {author_id} не найден'
            )
        comments = self.repository.get_by_author_id(author_id)
        return [CommentResponse.model_validate(comment) for comment in comments]