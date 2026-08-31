from sqlalchemy.orm import Session
from typing import List
from ..repositories import ProjectRepository, UserRepository, TaskRepository
from ..schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from ..schemas.user import UserResponse, UserBriefResponse
from fastapi import HTTPException, status
from ..enums import Status
from typing import Optional
from ..config import settings
import logging

logger = logging.getLogger(__name__)

class ProjectService:
    def __init__(self, project_repository: ProjectRepository, user_repository: UserRepository, task_repository: TaskRepository):
        self.repository = project_repository
        self.user_repository = user_repository
        self.task_repository = task_repository

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
        project_count = self.repository.count_by_owner(owner_id)
        if project_count >= settings.MAX_PROJECTS_PER_USER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Достигнуто максимальное число проектов')
        project = self.repository.create(project_data, owner_id)
        logger.info('Successfully created project, project_name = %s, owner_id = %s', project_data.name, owner_id)

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
            logger.info('Succesfully deleted project %s', project_id)
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

    def get_projects_for_user(self, user_id: int, skip: int = 0, limit: int = 10, status: Optional[Status] = None, q: Optional[str] = None) -> dict:
        projects = self.repository.get_my_projects_paginated(user_id, skip, limit, status, q)
        count_projects = self.repository.count_my_projects(user_id, status, q)
        return {
            'items': [ProjectResponse.model_validate(p) for p in projects],
            'total': count_projects,
            'skip': skip,
            'limit': limit
        }

    def update_members(self, project_id: int, member_ids: List[int], current_user_id: int) -> ProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Не существует такого проекта')
        if project.owner_id !=current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Только владелец проекта может менять участников проекта')
        for user_id in member_ids:
            if not self.user_repository.exists(user_id):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
        updated_project = self.repository.update_members(project_id, member_ids)
        return ProjectResponse.model_validate(updated_project)
        
    def get_all_members_in_project(self, project_id: int) -> List[UserBriefResponse]:
        if not self.repository.exists(project_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Такой проект не найден')
        members = self.repository.get_all_members_in_project(project_id)
        return [UserBriefResponse.model_validate(m) for m in members]

    def add_member(self, project_id: int, user_id: int, current_user_id: int) -> ProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден')
        if project.owner_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Только владелец может добавлять участников в проект')
        if not self.user_repository.exists(user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
        if any(m.id == user_id for m in project.members):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Такой пользователь уже есть в проекте')
        updated_project = self.repository.add_member(project_id, user_id)
        logger.info('Successfully added member %s in project %s', user_id, project_id)
        return ProjectResponse.model_validate(updated_project)

    def remove_member(self, project_id: int, user_id: int, current_user_id: int) -> ProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден')
        if project.owner_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Только владелец может удалять участников из проекта')
        if not self.user_repository.exists(user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не найден')
        if not any(m.id == user_id for m in project.members):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Такого пользователя нет в проекте')
        if user_id == project.owner_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Нельзя удалить владельца')
        updated_project = self.repository.remove_member(project_id, user_id)
        self.task_repository.remove_assignee_from_all_tasks(project_id, user_id)
        logger.info('Successfully removed member %s from project %s', user_id, project_id)
        return ProjectResponse.model_validate(updated_project)

    def leave_project(self, project_id: int, current_user_id: int) -> ProjectResponse:
        project = self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Проект не найден')
        if not any(m.id == current_user_id for m in project.members):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Пользователь не является участником проекта')
        if current_user_id == project.owner_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Нельзя выйти из проекта, если ты владелец')
        updated_project = self.repository.remove_member(project_id, current_user_id)
        self.task_repository.remove_assignee_from_all_tasks(project_id, current_user_id)
        return ProjectResponse.model_validate(updated_project)

    