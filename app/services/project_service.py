from sqlalchemy.orm import Session
from typing import List
from ..repositories.project_repository import ProjectRepository
from ..schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from fastapi import HTTPException, status

class ProjectService:
    def __init__(self, project_repository: ProjectRepository):
        self.repository = project_repository

    def get_all_project(self) -> List[ProjectResponse]:
        projects = self.repository.get_all()
        return [ProjectResponse.model_validate(project) for project in projects]

    def get_project_by_id(self, project_id: int) -> ProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Проект с id {project_id} не найден'
            )
        return ProjectResponse.model_validate(project)

    def project_create(self, project_data: ProjectCreate) -> ProjectResponse:
        project = self.repository.create(project_data)
        return ProjectResponse.model_validate(project)

    def get_multiple_project_by_id(self, project_ids: List[int]) -> List[ProjectResponse]:
        projects = self.repository.get_multiple_by_ids(project_ids)
        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Проекты с такими id не найдены"
            )
        return [ProjectResponse.model_validate(project) for project in projects]

    def update_project(self, project_id: int, project_data: ProjectUpdate) -> ProjectResponse:
        if not self.repository.exists(project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Проект с id {project_id} не найден'
            )

        if project_data.name:
            existing = self.repository.get_by_name(project_data.name)
            if existing and existing.id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Название {project_data.name} уже занято'
                )
        updated_project = self.repository.update(project_id, project_data)
        return ProjectResponse.model_validate(updated_project)

    def delete_project(self, project_id: int) -> None:
        if self.repository.delete(project_id):
            return
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Проект с id {project_id} не найден'
            )

    def get_by_name(self, name: str) -> ProjectResponse:
        project = self.repository.get_by_name(name)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Проект с названием {name} не найден'
            )
        return ProjectResponse.model_validate(project)