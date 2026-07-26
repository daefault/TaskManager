from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories import UserRepository, CommentRepository, NotificationRepository, ProjectRepository, TaskRepository
from app.services import UserService, CommentService, ProjectService, TaskService, NotificationService


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

def get_task_service(
        task_repo: TaskRepository = Depends(get_task_repository),
        user_repo: UserRepository = Depends(get_user_repository),
        project_repo: ProjectRepository = Depends(get_project_repository)
) -> TaskService:
    return TaskService(task_repo, user_repo, project_repo)

def get_comment_service(
        comment_repo: CommentRepository = Depends(get_comment_repository),
        user_repo: UserRepository = Depends(get_user_repository),
        task_repo: TaskRepository = Depends(get_task_repository)
        ) -> CommentService:
    return CommentService(comment_repo, user_repo, task_repo)

def get_notification_service(
        notification_repo: NotificationRepository = Depends(get_notification_repository),
        user_repo: UserRepository = Depends(get_user_repository)
) -> NotificationService:
    return NotificationService(notification_repo, user_repo)

def get_project_service(
        project_repo: ProjectRepository = Depends(get_project_repository),
        user_repo: UserRepository = Depends(get_user_repository)
) -> ProjectService:
    return ProjectService(project_repo, user_repo)

