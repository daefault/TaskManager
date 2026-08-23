from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Project, User
from .base import BaseRepository
from ..schemas.project import ProjectCreate, ProjectUpdate
from ..enums import Status


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db: Session):
        super().__init__(db, Project)

    def create(self, data: ProjectCreate, owner_id: int) -> Project:
        project_data = data.model_dump(exclude={'member_ids'})
        project_data['owner_id'] = owner_id
        db_project = Project(**project_data)

        owner = self.db.query(User).filter(User.id == owner_id).first()
        if owner:
            db_project.members.append(owner)

        if data.member_ids:
            members = self.db.query(User).filter(User.id.in_(data.member_ids)).all()
            db_project.members.extend(members)

        self.db.add(db_project) 
        self.db.commit()
        self.db.refresh(db_project)
        return db_project

    def count_by_owner(self, owner_id: int) -> int:
        return self.db.query(Project).filter(Project.owner_id == owner_id).count()

    def update_members(self, project_id: int, members_ids: List[int]) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        if project.owner_id not in members_ids:
            members_ids.append(project.owner_id)
        new_members = self.db.query(User).filter(User.id.in_(members_ids)).all()

        project.members = new_members
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_by_name(self, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.name == name).first()

    def get_by_user_and_name(self, user_id: int, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.owner_id == user_id, Project.name == name).first()

    def get_all_members_in_project(self, project_id: int) -> Optional[List[User]]:
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []
        return project.members

    def add_member(self, project_id: int, user_id: int) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if user not in project.members:
            project.members.append(user)
            self.db.commit()
            self.db.refresh(project)

        return project

    def remove_member(self, project_id: int, user_id: int) -> Optional[Project]:
        project = self.get_by_id(project_id)
        if not project:
            return None
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if user in project.members:
            project.members.remove(user)
            self.db.commit()
            self.db.refresh(project)

        return project

    def count_my_projects(self, user_id: int, status: Optional[Status] = None, q: Optional[str] = None) -> int:
        owner_ids = self.db.query(Project.id.label('id')).filter(Project.owner_id == user_id)
        member_ids = self.db.query(Project.id.label('id')).join(Project.members).filter(User.id == user_id)
        union = owner_ids.union(member_ids).subquery()
        query = self.db.query(Project).join(union, Project.id == union.c.id)
        if status is not None:
            query = query.filter(Project.status == status)
        if q is not None and q.strip():
            query = query.filter( 
            Project.name.ilike(f'%{q}%')
        )
        return query.count()

    def get_my_projects_paginated(
            self,
            user_id: int,
            skip: int = 0,
            limit: int = 10,
            status: Optional[Status] = None,
            q: Optional[str] = None
    ) -> List[Project]:
        owner_subquery = self.db.query(Project.id.label('id')).filter(Project.owner_id == user_id)
        member_subquery = self.db.query(Project.id.label('id')).join(Project.members).filter(User.id == user_id)
        union = owner_subquery.union(member_subquery).subquery()
        query = self.db.query(Project).join(union, Project.id == union.c.id)
        if status is not None:
            query = query.filter(Project.status == status)
        if q is not None and q.strip():
            query = query.filter( 
            Project.name.ilike(f'%{q}%')
        )
        return query.order_by(Project.created_at.desc()).offset(skip).limit(limit).all()