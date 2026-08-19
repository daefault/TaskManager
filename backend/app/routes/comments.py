from fastapi import APIRouter, Depends, status, Query, HTTPException, status
from typing import List
from ..dependencies import get_comment_service, get_task_service, get_current_user, require_admin, get_project_service
from ..services import CommentService, TaskService, ProjectService
from ..schemas.comment import CommentResponse, CommentCreate, CommentUpdate
from ..models import User
from ..config import settings

router = APIRouter(
    prefix='/comments',
    tags=['comments']
)

@router.get('', response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
def get_all_comments(service: CommentService = Depends(get_comment_service), admin: User = Depends(require_admin)):
    return service.get_all_comment()

@router.post('', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreate, 
    service: CommentService = Depends(get_comment_service), 
    current_user: User = Depends(get_current_user)
):
    if service.count_comments_by_user(current_user.id) >= settings.MAX_COMMENTS_PER_USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Превышено максимальное число комментариев на пользователя')
    return service.create_comment(comment_data, current_user.id)

@router.get('/by_author/', response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
def get_comment_by_author(
    author_id: int = Query(..., description='id пользователя'),
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin and current_user.id !=author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    return service.get_comments_by_author(author_id)

@router.get('/{comment_id}', response_model=CommentResponse, status_code=status.HTTP_200_OK)
def get_comment_by_id(
    comment_id: int, 
    service: CommentService = Depends(get_comment_service), 
    admin: User = Depends(require_admin)
):
    return service.get_comment_by_id(comment_id)

@router.put('/{comment_id}', response_model=CommentResponse, status_code=status.HTTP_200_OK)
def update_comment(
    comment_id: int, 
    comment_data: CommentUpdate, 
    service: CommentService = Depends(get_comment_service),
    current_user: User = Depends(get_current_user)
):
    comment = service.get_comment_by_id(comment_id)
    if current_user.id != comment.author_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    return service.update_comment(comment_id, comment_data)

@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int, 
    service: CommentService = Depends(get_comment_service),
    project_service: ProjectService = Depends(get_project_service),
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
    ):
    comment = service.get_comment_by_id(comment_id)
    task = task_service.get_task_by_id(comment.task_id)
    project = project_service.get_project_by_id(task.project_id)
    if not current_user.is_admin and comment.author_id != current_user.id and current_user.id != project.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    service.delete_comment(comment_id)

@router.get('/task/{task_id}', response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
def get_comments_by_task(
    task_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=10, le=100),
    service: CommentService = Depends(get_comment_service),
    task_service: TaskService = Depends(get_task_service),
    current_user: User = Depends(get_current_user)
):
    task = task_service.get_task_by_id(task_id)
    if not current_user.is_admin and not current_user.id in [a.id for a in task.assignees] and current_user.id != task.creator_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Недостаточно прав для выполнения операции'
        )
    return service.get_comments_by_task(task_id, skip, limit)