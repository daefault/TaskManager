from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.task import Task
from .base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db:Session):
        super().__init__(db, Task)

    def get_by_title(self, title: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.title == title).first()
