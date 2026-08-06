from sqlalchemy.orm import Session
from typing import List
from ..repositories import ProjectRepository, UserRepository
from ..schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from ..schemas.user import UserResponse, UserBriefResponse
from fastapi import HTTPException, status
from ..enums import Status
from typing import Optional



class ProjectService:
    def __init__(self, project_repository: ProjectRepository, user_repository: UserRepository):
        self.repository = project_repository
        self.user_repository = user_repository

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
        project_response = ProjectResponse.model_validate(project)
        members = self.repository.get_all_members_in_project(project_id)
        project_response.members = [UserBriefResponse.model_validate(m) for m in members]
        return project_response

    def create_project(self, project_data: ProjectCreate, owner_id: int) -> ProjectResponse:
        if not self.user_repository.exists(owner_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Пользователь с id {project_data.owner_id} не найден'
            )
        existing = self.repository.get_by_user_and_name(owner_id, project_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Проект с названием {project_data.name} уже существует у пользователя {owner_id}'
            )
        if project_data.member_ids:
            for user_id in project_data.member_ids:
                if not self.user_repository.exists(user_id):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f'Пользователь с id {user_id} не найден'
                    )
        project = self.repository.create(project_data, owner_id)
        return ProjectResponse.model_validate(project)

    def update_project(self, project_id: int, project_data: ProjectUpdate) -> ProjectResponse:
        if not self.repository.exists(project_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Проект с id {project_id} не найден'
            )

        if project_data.name:
            current_project = self.repository.get_by_id(project_id)
            owner_id = current_project.owner_id
            name = project_data.name
            existing = self.repository.get_by_user_and_name(owner_id, name)
            if existing and existing.id != project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Проект с названием {name} уже существует у пользователя'
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

    def get_projects_for_user(self, user_id: int, skip: int = 0, limit: int = 10, status: Optional[Status] = None) -> List[ProjectResponse]:
        projects = self.repository.get_by_owner(user_id) + self.repository.get_by_member(user_id)
        unique_projects = list({p.id: p for p in projects}.values())
        unique_projects.sort(key=lambda p: p.created_at, reverse=True)
        if status is not None:
            unique_projects = [p for p in unique_projects if p.status == status]
        paginated = unique_projects[skip:skip + limit]
        return [ProjectResponse.model_validate(p) for p in paginated]



    def add_members(self, project_id: int, user_ids: List[int], current_user_id: int) -> ProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Проект не найден'
            )
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Только владелец проекта может добавлять участников'
            )
        for user_id in user_ids:
            if not self.user_repository.exists(user_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Пользователя {user_id} не существует'
                )
        updated_project = self.repository.add_members(project_id, user_ids)
        return ProjectResponse.model_validate(updated_project)

    def remove_members(self, project_id: int, user_ids: List[int], current_user_id: int) -> ProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Проект не найден'
            )
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Только владелец проекта может удалять участников'
            )
        for user_id in user_ids:
            if not self.user_repository.exists(user_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Пользователя {user_id} не существует'
                )
        if project.owner_id in user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Нельзя удалить владельца проекта'
            )
        project_member_ids = [member.id for member in project.members]
        for user_id in user_ids:
            if user_id not in project_member_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Пользователь {user_id} не участник проекта'
                )
        updated_project = self.repository.remove_members(project_id, user_ids)
        return ProjectResponse.model_validate(updated_project)

    def get_all_members_in_project(self, project_id: int) -> List[UserBriefResponse]:
        if not self.repository.exists(project_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Такой проект не найден')
        members = self.repository.get_all_members_in_project(project_id)
        return [UserBriefResponse.model_validate(m) for m in members]