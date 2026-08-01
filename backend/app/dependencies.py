from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories import UserRepository, CommentRepository, NotificationRepository, ProjectRepository, TaskRepository
from app.services import UserService, CommentService, ProjectService, TaskService, NotificationService, AuthService
from app.models import User
from app.security import decode_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security_scheme = HTTPBearer(auto_error=False)


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

def get_auth_service(    
        user_repo: UserRepository = Depends(get_user_repository),
        user_service: UserService = Depends(get_user_service)
) -> AuthService:
    return AuthService(user_repo, user_service)


#Зависимости для проверки на права администратора
def get_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
        user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    if not credentials: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Не авторизован',
            headers={'WWW-Authenticate':'Bearer'}
        )
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Невалидный токен',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    if payload.get('type') != 'access':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный тип токена',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    user_id = payload.get('sub')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный payload токена',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    user = user_repo.get_by_id(int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Пользователь не найден',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Учётная запись отключена'
        )
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Требуются права администратора'
        )
    return current_user