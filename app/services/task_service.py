from sqlalchemy.orm import Session
from typing import List
from ..repositories.task_repository import TaskRepository
from ..schemas.task import TaskResponse, TaskCreate, TaskUpdate
from fastapi import HTTPException, status

class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.repository = task_repository

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

    def task_create(self, task_data: TaskCreate) -> TaskResponse:
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

        if task_data.title:
            existing = self.repository.get_by_title(task_data.title)
            if existing and existing.id != task_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Название {task_data.title} уже занято'
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