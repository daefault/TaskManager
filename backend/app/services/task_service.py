from sqlalchemy.orm import Session
from typing import List
from ..repositories import TaskRepository, UserRepository, ProjectRepository
from ..schemas.task import TaskResponse, TaskCreate, TaskUpdate
from ..services.notification_service import NotificationService
from fastapi import HTTPException, status
from typing import Optional, Union, Literal
from ..schemas.user import UserResponse
from ..enums import TaskStatus, Priority
from ..config import settings


class TaskService:
    def __init__(
            self, 
            task_repository: TaskRepository,
            user_repository: UserRepository,
            project_repository: ProjectRepository,
            notification_service: NotificationService
            ):
        self.repository = task_repository
        self.user_repository = user_repository
        self.project_repository = project_repository
        self.notification_service = notification_service

    def get_all_tasks_for_user(
            self,
            user_id: int,
            skip: int = 0, 
            limit: int = 100,
            project_id: Optional[int] = None,
            status: Optional[Union[TaskStatus, Literal['active']]] = None,
            priority: Optional[Priority] = None,
            is_project_owner: bool = False,
            query: Optional[str] = None
    ) -> dict:
        tasks = self.repository.get_for_user(user_id, skip, limit, project_id, status, priority, is_project_owner, query)
        task_count = self.repository.count_my_tasks(user_id, project_id, status, priority, is_project_owner, query)
        return {
            'items': [TaskResponse.model_validate(t) for t in tasks],
            'total': task_count,
            'limit': limit,
            'skip': skip
        }

    def get_task_by_id(self, task_id: int) -> TaskResponse:
        task = self.repository.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найден'
            )
        return TaskResponse.model_validate(task)

    def create_task(self, task_data: TaskCreate, creator_id: int) -> TaskResponse:
        if not self.project_repository.exists(task_data.project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Проект с id {task_data.project_id} не найден'
            )

        if not self.user_repository.exists(creator_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {creator_id} не найден'
            )

        existing = self.repository.get_by_title_in_project(
            task_data.project_id, task_data.title
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Задача с названием {task_data.title} уже существует в проекте {task_data.project_id}'
            )

        if task_data.assignee_ids:
            project = self.project_repository.get_by_id(task_data.project_id)
            project_member_ids = [m.id for m in project.members]
            for user_id in task_data.assignee_ids:
                if not self.user_repository.exists(user_id):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'Пользователь с id {user_id} не найден'
                    )
                if user_id not in project_member_ids:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'Пользователь {user_id} не является участником проекта'
                    )
        if self.repository.count_by_creator(creator_id) >= settings.MAX_TASKS_PER_USER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Превышено максимальное число задач на пользователя')
        if self.repository.count_by_project(task_data.project_id) >= settings.MAX_TASKS_PER_PROJECT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Превышено максимальное число задач на проект')
        task = self.repository.create(task_data, creator_id)
        if task_data.assignee_ids:
            for user_id in task_data.assignee_ids:
                self.notification_service.notify_task_assigned(
                    user_id=user_id,
                    task_title=task.title
                )
        return TaskResponse.model_validate(task)

    def update_task(self, task_id: int, task_data: TaskUpdate) -> TaskResponse:
        if not self.repository.exists(task_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найден'
            )
        
        if task_data.title or task_data.project_id:
            current_task=self.repository.get_by_id(task_id)
            project_id = task_data.project_id if task_data.project_id else current_task.project_id
            title = task_data.title if task_data.title else current_task.title
            existing = self.repository.get_by_title_in_project(project_id, title)
            if existing and existing.id != task_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Задача с названием {title} уже существует в этом проекте'
                )

        if task_data.project_id:
            if not self.project_repository.exists(task_data.project_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Проект с id {task_data.project_id} не найден'
                )
        updated_task = self.repository.update(task_id, task_data)
        return TaskResponse.model_validate(updated_task)

    def delete_task(self, task_id: int) -> None:
        if self.repository.delete(task_id):
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найден'
            )

    def get_by_title(self, title: str) -> TaskResponse:
        task = self.repository.get_by_title(title)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с названием {title} не найдена'
            )
        return TaskResponse.model_validate(task)

    def add_assignee(self, task_id: int, user_id: int) -> TaskResponse:
        task = self.repository.get_by_id(task_id)
        if not task: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найдена')
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        project = self.project_repository.get_by_id(task.project_id)
        project_member_ids = [m.id for m in project.members]
        if user_id not in project_member_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Пользователь {user_id} не участник проекта'
            )
        task = self.repository.add_assignee(task_id, user_id)
        self.notification_service.notify_task_assigned(
            user_id=user_id, 
            task_title=task.title
        )
        return TaskResponse.model_validate(task)

    def remove_assignee(self, task_id: int, user_id: int) -> TaskResponse:
        if not self.repository.exists(task_id):
            raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'Задача с id {task_id} не найдена'
                    )
        if not self.user_repository.exists(user_id):
            raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'Пользователь с id {user_id} не найден'
                    )
        task = self.repository.remove_assignee(task_id, user_id)
        return TaskResponse.model_validate(task)

    def get_assigned_tasks(self, user_id: int) -> List[TaskResponse]:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {user_id} не найден'
            )
        tasks = user.assigneed_tasks
        return [TaskResponse.model_validate(task) for task in tasks]

    def update_assignees(self, task_id: int, assignee_ids: List[int]) -> TaskResponse:
        task = self.repository.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найдена')
        project = self.project_repository.get_by_id(task.project_id)
        project_member_ids = [m.id for m in project.members]
        for user_id in assignee_ids:
            if user_id not in project_member_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Пользователь {user_id} не участник проекта'
            )
        task = self.repository.update_assignees(task_id, assignee_ids)
        for user_id in assignee_ids:
            self.notification_service.notify_task_assigned(
                    user_id=user_id,
                    task_title=task.title
            )
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Задача не найдена')
        return TaskResponse.model_validate(task)

    def get_task_assignees(self, task_id: int) -> List[UserResponse]:
        assignees = self.repository.get_task_assignees(task_id)
        return [UserResponse.model_validate(a) for a in assignees]
