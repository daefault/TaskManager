from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Project
from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db:Session):
        super().__init__(db, Project)

    def get_by_name(self, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.name == name).first()

    def get_by_user_and_name(self, user_id: int, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.owner_id == user_id, Project.name == name).first()
