from fastapi import APIRouter, Depends, status, Query, status, HTTPException
from typing import List
from ..dependencies import get_project_service, get_current_user, require_admin
from ..services import ProjectService
from ..schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate, UpdateMembersRequest
from ..schemas.user import UserBriefResponse
from ..models import User
from ..enums import Status
from typing import Optional


router = APIRouter(
    prefix='/projects',
    tags=['projects']
)

@router.get('', response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def get_my_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, le=100),
    status: Optional[Status] = Query(None, decsription='Статус проекта (active или archived)'),
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    return service.get_projects_for_user(current_user.id, skip, limit, status)

@router.get('/all', response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def get_all_projects(service: ProjectService = Depends(get_project_service), admin: User = Depends(require_admin)):
    return service.get_all_project()

@router.post('', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
      service: ProjectService = Depends(get_project_service),
      current_user: User = Depends(get_current_user)):
    return service.create_project(project_data, current_user.id)

@router.get('/by-name/', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project_by_name(
    name: str = Query(..., min_length=1, max_length=100, description='Название проекта'),
    service: ProjectService = Depends(get_project_service),
    current_user: User = Depends(get_current_user)
):
    project = service.get_by_name(name)
    if project.owner_id != current_user.id and not current_user.is_admin:
        is_member = any(m.id == current_user.id for m in project.members)
        if not is_member:
            raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Нет доступа к этому проекту'
                )
    return project

@router.put('/{project_id}', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_project(
    project_id: int, 
    project_data: ProjectUpdate, 
    service: ProjectService = Depends(get_project_service), 
    current_user: User = Depends(get_current_user)):
    project = service.get_project_by_id(project_id)
    if project.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для обновления проекта'
        )

    return service.update_project(project_id, project_data)

@router.delete('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int, 
    service: ProjectService = Depends(get_project_service), 
    current_user: User = Depends(get_current_user)):
    project = service.get_project_by_id(project_id)
    if project.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для удаления проекта'
        )
    service.delete_project(project_id)

@router.get('/{project_id}', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project_by_id(
    project_id: int, 
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    project = service.get_project_by_id(project_id)
    if project.owner_id != current_user.id and not current_user.is_admin:
        is_member = any(m.id == current_user.id for m in project.members)
        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Нет доступа к этому проекту'
            )
    return project

@router.put('/{project_id}/members', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_members_in_project(
    project_id: int, 
    request: UpdateMembersRequest,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    return service.update_members(project_id, request.member_ids, current_user.id)

@router.get('/{project_id}/members', response_model=List[UserBriefResponse], status_code=status.HTTP_200_OK)
def get_all_members_in_project(
    project_id: int, 
    current_user: User = Depends(get_current_user), 
    service: ProjectService = Depends(get_project_service)
):
    project = service.get_project_by_id(project_id)
    if project.owner_id != current_user.id and current_user.id not in [m.id for m in project.members]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='У вас нет доступа к этому проекту')
    return service.get_all_members_in_project(project_id)

@router.post('/{project_id}/members/{user_id}', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def add_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    return service.add_member(project_id, user_id, current_user.id)

@router.delete('/{project_id}/members/{user_id}', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def remove_member(
    project_id: int, 
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: ProjectService = Depends(get_project_service)
):
    return service.remove_member(project_id, user_id, current_user.id)
