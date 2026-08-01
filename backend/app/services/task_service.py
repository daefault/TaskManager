from sqlalchemy.orm import Session
from typing import List
from ..repositories import TaskRepository, UserRepository, ProjectRepository
from ..schemas.task import TaskResponse, TaskCreate, TaskUpdate
from fastapi import HTTPException, status

class TaskService:
    def __init__(
            self, 
            task_repository: TaskRepository,
            user_repository: UserRepository,
            project_repository: ProjectRepository
            ):
        self.repository = task_repository
        self.user_repository = user_repository
        self.project_repository = project_repository

    def get_all_task(self) -> List[TaskResponse]:
        tasks = self.repository.get_all()
        return [TaskResponse.model_validate(task) for task in tasks]

    def get_task_by_id(self, task_id: int) -> TaskResponse:
        task = self.repository.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найден'
            )
        return TaskResponse.model_validate(task)

    def create_task(self, task_data: TaskCreate) -> TaskResponse:
        if not self.project_repository.exists(task_data.project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Проект с id {task_data.project_id} не найден'
            )

        if not self.user_repository.exists(task_data.creator_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {task_data.creator_id} не найден'
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
            for user_id in task_data.assignee_ids:
                if not self.user_repository.exists(user_id):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'Пользователь с id {user_id} не найден'
                    )
        task = self.repository.create(task_data)
        return TaskResponse.model_validate(task)

    def get_multiple_task_by_id(self, task_ids: List[int]) -> List[TaskResponse]:
        tasks = self.repository.get_multiple_by_ids(task_ids)
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Задачи с такими id не найдены"
            )
        return [TaskResponse.model_validate(task) for task in tasks]

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

        if task_data.creator_id:
            if not self.user_repository.exists(task_data.creator_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Пользователь с id {task_data.creator_id} не найден'
                )

        if task_data.assignee_ids:
            for user_id in task_data.assignee_ids:
                if not self.user_repository.exists(user_id):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'Пользователь с id {user_id} не найден'
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
        task = self.repository.add_assignee(task_id, user_id)
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

    