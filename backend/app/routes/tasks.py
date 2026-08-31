from fastapi import APIRouter, Depends, status, Query, HTTPException, status
from typing import List
from ..dependencies import get_task_service, get_current_user, require_admin, get_project_service
from ..services import TaskService, ProjectService
from ..schemas.task import TaskResponse, TaskCreate, TaskUpdate, UpdateAssigneesRequest
from ..models import User
from typing import Optional, Union, Literal
from ..enums import TaskStatus, Priority
from ..schemas.user import UserResponse

router = APIRouter(
    prefix='/tasks',
    tags=['tasks']
)

@router.get('', response_model=dict, status_code=status.HTTP_200_OK)
def get_my_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, le=100),
    project_id: Optional[int] = None,
    status: Optional[Union[TaskStatus, Literal['active']]] = Query(None, description='Фильтр по статусу задачи'),
    priority: Optional[Priority] = Query(None, description='Фильтр по приоритету задачи'),
    q: Optional[str] = Query(None, max_length=100, description='Строка для поиска по названию задачи'),
    service: TaskService = Depends(get_task_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    is_project_owner = False
    if project_id is not None:
        project = project_service.get_project_by_id(project_id)
        if project.owner_id == current_user.id:
            is_project_owner = True
    status_enum = None
    if status == 'active':
        status_enum = 'active'
    elif status is not None:
        try:
            status_enum = TaskStatus(status)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Некорректный статус задачи')
    return service.get_all_tasks_for_user(current_user.id, skip, limit, project_id, status_enum, priority, is_project_owner, q)

@router.get('/by-title/', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_title(
    title: str = Query(..., min_length=1, max_length=200, description='Название задачи'),
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)):
    task = service.get_by_title(title)
    if task.creator_id != current_user.id and current_user.id not in [assignee.id for assignee in task.assignees]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='У вас нет доступа к этой задаче')
    return service.get_by_title(title)


@router.get('/{task_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def get_task_by_id(task_id: int, service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    return service.get_task_by_id(task_id)

@router.get('/{task_id}/assignees', response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_task_assignees(task_id: int, service: TaskService = Depends(get_task_service), current_user: User = Depends(get_current_user)):
    return service.get_task_assignees(task_id)

@router.get('/assigned/{user_id}', response_model=List[TaskResponse], status_code=status.HTTP_200_OK)
def get_assigned_tasks(
    current_user: User = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
    ):
    return service.get_assigned_tasks(current_user.id)

@router.post('', response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate, 
    service: TaskService = Depends(get_task_service), 
    current_user: User = Depends(get_current_user)
    ):
    return service.create_task(task_data, current_user.id)

@router.put('/{task_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_task(
    task_id: int, 
    task_data: TaskUpdate, 
    service: TaskService = Depends(get_task_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
    ):
    task = service.get_task_by_id(task_id)
    project = project_service.get_project_by_id(task.project_id)
    if current_user.id != task.creator_id and current_user.id != project.owner_id and not current_user.id in [a.id for a in task.assignees]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    return service.update_task(task_id, task_data)

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int, 
    service: TaskService = Depends(get_task_service),
    project_service: ProjectService = Depends(get_project_service), 
    current_user: User = Depends(get_current_user)):
    task = service.get_task_by_id(task_id)
    project = project_service.get_project_by_id(task.project_id)
    if current_user.id != task.creator_id and not current_user.is_admin and current_user.id != project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    service.delete_task(task_id)

@router.put('/{task_id}/assignees', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def update_assignees(
    task_id: int, 
    request: UpdateAssigneesRequest, 
    current_user: User = Depends(get_current_user),
    project_service: ProjectService = Depends(get_project_service),
    service: TaskService = Depends(get_task_service)
):
    task = service.get_task_by_id(task_id)
    project = project_service.get_project_by_id(task.project_id)
    if current_user.id != task.creator_id and not current_user.is_admin and current_user.id != project.owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Нет прав на управление исполнителями')
    return service.update_assignees(task_id, request.assignee_ids)

@router.post('/{task_id}/assignees/{user_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def add_assignee(
    task_id: int, 
    user_id: int, 
    service: TaskService = Depends(get_task_service), 
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    task = service.get_task_by_id(task_id)
    project = project_service.get_project_by_id(task.project_id)
    if current_user.id != task.creator_id and current_user.id != project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    return service.add_assignee(task_id, user_id)

@router.delete('/{task_id}/assignees/{user_id}', response_model=TaskResponse, status_code=status.HTTP_200_OK)
def remove_assignee(
    task_id: int, 
    user_id: int, 
    service: TaskService = Depends(get_task_service),
    project_service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
    ):
    task = service.get_task_by_id(task_id)
    project = project_service.get_project_by_id(task.project_id)
    if current_user.id != task.creator_id and current_user.id != project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    return service.remove_assignee(task_id, user_id)
