from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Task, User
from .base import BaseRepository
from ..schemas.task import TaskCreate, TaskUpdate

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db:Session):
        super().__init__(db, Task)

    def create(self, data: TaskCreate, creator_id: int) -> Task:
        task_data = data.model_dump(exclude={'assignee_ids'})
        task_data['creator_id'] = creator_id
        db_task = Task(**task_data)
        if data.assignee_ids:
            assignees = self.db.query(User).filter(
                User.id.in_(data.assignee_ids)
            ).all()
            db_task.assignees = assignees

        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def get_by_title(self, title: str) -> Optional[Task]:
        return self.db.query(Task).filter(Task.title == title).first()

    def add_assignee(self, task_id: int, user_id: int) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task:
            return None

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        if user not in task.assignees:
            task.assignees.append(user)
            self.db.commit()
            self.db.refresh(task)
        return task

    def remove_assignee(self, task_id: int, user_id: int) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task: 
            return None

        user = self.db.query(User).filter(User.id == user_id).first()
        if user and user in task.assignees:
            task.assignees.remove(user)
            self.db.commit()
            self.db.refresh(task)

        return task

    def get_by_title_in_project(self, project_id: int, title: str) -> Optional[Task]:
        return self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.title == title
        ).first()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 10) -> List[Task]:
        creator_query = self.db.query(Task.id.label('id')).filter(Task.creator_id == user_id)
        assignee_query = self.db.query(Task.id.label('id')).join(Task.assignees).filter(User.id == user_id)

        union = creator_query.union(assignee_query).subquery()

        return self.db.query(Task).join(union, Task.id == union.c.id).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()

    def update_assignees(self, task_id: int, assignee_ids: List[int]) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task: 
            return None

        assignees = self.db.query(User).filter(User.id.in_(assignee_ids)).all()
        task.assignees = assignees

        self.db.commit()
        self.db.refresh(task)
        return task