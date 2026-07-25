from sqlalchemy.orm import Session
from typing import List
from ..repositories.comment_repository import CommentRepository
from ..schemas.comment import CommentResponse, CommentCreate, CommentUpdate
from fastapi import HTTPException, status

class CommentService:
    def __init__(self, comment_repository: CommentRepository):
        self.repository = comment_repository

    def get_all_comment(self) -> List[CommentResponse]:
        comments = self.repository.get_all()
        return [CommentResponse.model_validate(comment) for comment in comments]

    def get_comment_by_id(self, comment_id: int) -> CommentResponse:
        comment = self.repository.get_by_id(comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Комментарии с id {comment_id} не найден'
            )
        return CommentResponse.model_validate(comment)

    def comment_create(self, comment_data: CommentCreate) -> CommentResponse:
        comment = self.repository.create(comment_data)
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