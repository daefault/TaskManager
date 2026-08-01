from .comments import router as comment_router
from .notifications import router as notification_router
from .projects import router as project_router
from .tasks import router as task_router
from .users import router as user_router
from .auth import router as auth_router

__all__ = [
    'comment_router',
    'notification_router',
    'project_router',
    'task_router',
    'user_router',
    'auth_router'
           ]