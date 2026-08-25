from sqlalchemy.orm import Session
from typing import List, Optional, Union, Literal
from ..models import Task, User
from .base import BaseRepository
from ..schemas.task import TaskCreate, TaskUpdate
from ..enums import TaskStatus, Priority
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta, timezone


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

    def update_assignees(self, task_id: int, assignee_ids: List[int]) -> Optional[Task]:
        task = self.get_by_id(task_id)
        if not task: 
            return None

        assignees = self.db.query(User).filter(User.id.in_(assignee_ids)).all()
        task.assignees = assignees

        self.db.commit()
        self.db.refresh(task)
        return task

    def get_for_user(
            self, 
            user_id: int, 
            skip: int = 0,
            limit: int = 100, 
            project_id: Optional[int] = None,
            status: Optional[Union[TaskStatus, Literal['active']]] = None, 
            priority: Optional[Priority] = None,
            is_project_owner: bool = False,
            q: Optional[str] = None
        ) -> List[Task]:
        query = self.db.query(Task)
        if is_project_owner:
            query = query.filter(Task.project_id == project_id)
        else:
            query = query.filter(
            (Task.creator_id == user_id) |
            (Task.assignees.any(User.id == user_id))
            )
        if project_id is not None:
            query = query.filter(Task.project_id == project_id)
        if status is not None:
            if status == 'active':
                query = query.filter(
                    (Task.status != TaskStatus.DONE) & 
                    (Task.status != TaskStatus.CANCELLED) &
                    (Task.status != TaskStatus.OVERDUE)
                    )
            else:
                query = query.filter(Task.status == status)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        if q is not None and q.strip():
            query = query.filter(
                (Task.title.ilike(f'%{q}%'))
            )
        query = query.order_by(Task.created_at.desc())
        return query.offset(skip).limit(limit).all()

    def count_my_tasks(
            self,
            user_id: int,
            project_id: Optional[int] = None,
            status: Optional[Union[TaskStatus, Literal['active']]] = None,
            priority: Optional[Priority] = None,
            is_project_owner: bool = False,
            q: Optional[str] = None
    ) -> int:
        query = self.db.query(Task)
        if is_project_owner:
            query = query.filter(Task.project_id == project_id)
        else:
            query = query.filter(
            (Task.creator_id == user_id) | 
            (Task.assignees.any(User.id == user_id))
            )
        if project_id is not None:
            query = query.filter(Task.project_id == project_id)
        if status is not None:
            if status == 'active':
                query = query.filter(
                    (Task.status != TaskStatus.DONE) &
                    (Task.status != TaskStatus.CANCELLED) &
                    (Task.status != TaskStatus.OVERDUE)
                )
            else:
                query = query.filter(Task.status == status)
        if priority is not None:
            query = query.filter(Task.priority == priority)
        if q is not None and q.strip():
                query = query.filter(
                    (Task.title.ilike(f'%{q}%'))
                )
        return query.count()

    def get_task_assignees(self, task_id: int) -> List[User]:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task: 
            return []
        return task.assignees
    
    def remove_assignee_from_all_tasks(self, project_id: int, user_id: int):
        tasks = self.db.query(Task).filter(Task.project_id == project_id).all()
        if not tasks:
            return None
        for task in tasks: 
            if user_id in [a.id for a in task.assignees]:
                task.assignees = [a for a in task.assignees if a.id != user_id]
        self.db.commit()

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).options(
            selectinload(Task.creator)
        ).filter(Task.id == task_id).first()

    def count_by_creator(self, creator_id: int) -> int:
        return self.db.query(Task).filter(Task.creator_id == creator_id).count()

    def count_by_project(self, project_id: int) -> int:
        return self.db.query(Task).filter(Task.project_id == project_id).count()

    def check_overdue_task(self) -> List[Task]:
        now = datetime.now(timezone.utc)
        tasks = self.db.query(Task).filter(
            Task.deadline.isnot(None),
            Task.deadline < now,
            Task.status.notin_([TaskStatus.DONE, TaskStatus.CANCELLED, TaskStatus.OVERDUE])
        ).all()
        
        for task in tasks:
            task.status = TaskStatus.OVERDUE
        self.db.commit()
        return tasks
        