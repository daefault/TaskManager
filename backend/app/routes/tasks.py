from fastapi import APIRouter, Depends, status, Query
from typing import List
from ..dependencies import get_task_service
from ..services import TaskService
from ..schemas.task import TaskResponse, TaskCreate, TaskUpdate

router = APIRouter(
    prefix='/tasks',
    tags=['tasks']
)

@router.get('', response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_all_tasks(service: TaskService = Depends(get_task_service)):
    return service.get_all_task()

@router.get('/{task_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_id(task_id: int, service: TaskService = Depends(get_task_service)):
    return service.get_task_by_id(task_id)

@router.get('/by-title/', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_title(
    title: str = Query(..., min_length=1, max_length=200, description='Название задачи'),
    service: TaskService = Depends(get_task_service)):
    return service.get_by_title(title)

@router.get('/assigned/{user_id}', response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_assigned_tasks(user_id: int, service: TaskService = Depends(get_task_service)):
    return service.get_assigned_tasks(user_id)

@router.post('', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_data: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(task_data)

@router.put('/{task_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_data: TaskUpdate, service: TaskService = Depends(get_task_service)):
    return service.update_task(task_id, task_data)

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    return service.delete_task(task_id)

@router.post('/{task_id}/assignees/{user_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def add_assignee(task_id: int, user_id: int, service: TaskService = Depends(get_task_service)):
    return service.add_assignee(task_id, user_id)

@router.delete('/{task_id}/assignees/{user_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def remove_assignee(task_id: int, user_id: int, service: TaskService = Depends(get_task_service)):
    return service.remove_assignee(task_id, user_id)
