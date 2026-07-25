from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories import UserRepository, CommentRepository, NotificationRepository, ProjectRepository, TaskRepository
from app.services import UserService


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_comment_repository(db: Session = Depends(get_db)) -> CommentRepository:
    return CommentRepository(db)

def get_notification_repository(db: Session = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)

def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)

def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo)