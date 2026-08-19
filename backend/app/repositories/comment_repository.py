from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Comment
from .base import BaseRepository
from ..schemas.comment import CommentCreate
from sqlalchemy.orm import selectinload


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(db, Comment)

    def get_by_task_id(self, task_id: int, skip: int = 0, limit: int = 10) -> List[Comment]:
        return self.db.query(Comment).options(
            selectinload(Comment.author)
        ).filter(Comment.task_id == task_id).order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_author_id(self, author_id: int) -> List[Comment]:
        return self.db.query(Comment).filter(Comment.author_id == author_id).all()

    def create(self, data: CommentCreate, author_id: int) -> Comment:
        comment_data = data.model_dump()
        comment_data['author_id'] = author_id
        db_comment = Comment(**comment_data)
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment

    def count_comments_by_author(self, author_id: int) -> int:
        return self.db.query(Comment).filter(Comment.author_id == author_id).count()