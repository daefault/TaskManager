from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.project import Project
from ..schemas.project import ProjectCreate
from .base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db:Session):
        super().__init__(db, Project)

    def get_by_name(self, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.name == name).first()

