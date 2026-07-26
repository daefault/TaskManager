from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Task, User
from .base import BaseRepository
from ..schemas.task import TaskCreate, TaskUpdate

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db:Session):
        super().__init__(db, Task)

    def create(self, data: TaskCreate) -> Task:
        task_data = data.model_dump(exclude={'assignee_ids'})
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

    def update(self, id: int, data: TaskUpdate) -> Optional[Task]:
        if not self.exists(id):
            return None

        to_update = self.db.query(Task).filter(Task.id == id).first()
        update_data = data.model_dump(exclude_unser=True, exclude={'assignee_ids'})
        for key, value in update_data.items():
            if hasattr(to_update, key):
                setattr(to_update, key, value)
        if data.assignee_ids is not None:
            assignees = self.db.query(User).filter(
                User.id.in_(data.assignee_ids)
                ).all()
            to_update.assignees = assignees
        self.db.commit()
        self.db.refresh(to_update)
        return to_update
    
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
            self.db.commit()
            self.db.refresh(task)

        return task

    def get_by_title_in_project(self, project_id: int, title: str) -> Optional[Task]:
        return self.db.query(Task).filter(
            Task.project_id == project_id,
            Task.title == title
        ).first()