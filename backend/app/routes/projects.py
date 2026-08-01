from fastapi import APIRouter, Depends, status, Query
from typing import List
from ..dependencies import get_project_service
from ..services import ProjectService
from ..schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate

router = APIRouter(
    prefix='/projects',
    tags=['projects']
)

@router.get('', response_model=List[ProjectResponse], status_code=status.HTTP_200_OK)
def get_all_projects(service: ProjectService = Depends(get_project_service)):
    return service.get_all_project()

@router.get('/{project_id}', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project_by_id(project_id: int, service: ProjectService = Depends(get_project_service)):
    return service.get_project_by_id(project_id)

@router.get('/by-name/', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def get_project_by_name(
    name: str = Query(..., min_length=1, max_length=100, description='Название проекта'),
    service: ProjectService = Depends(get_project_service)
):
    return service.get_by_name(name)

@router.post('', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, service: ProjectService = Depends(get_project_service)):
    return service.create_project(project_data)

@router.put('/{project_id}', response_model=ProjectResponse, status_code=status.HTTP_200_OK)
def update_project(project_id: int, project_data: ProjectUpdate, service: ProjectService = Depends(get_project_service)):
    return service.update_project(project_id, project_data)

@router.delete('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, service: ProjectService = Depends(get_project_service)):
    return service.delete_project(project_id)
