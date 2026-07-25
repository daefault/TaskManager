from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.comment import Comment
from .base import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db:Session):
        super().__init__(db, Comment)

