from fastapi import APIRouter, Depends, status, Query
from typing import List
from ..dependencies import get_comment_service
from ..services import CommentService
from ..schemas.comment import CommentResponse, CommentCreate, CommentUpdate

router = APIRouter(
    prefix='/comments',
    tags=['comments']
)

@router.get('', response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
def get_all_comments(service: CommentService = Depends(get_comment_service)):
    return service.get_all_comment()

@router.get('/{comment_id}', response_model=CommentResponse, status_code=status.HTTP_200_OK)
def get_comment_by_id(comment_id: int, service: CommentService = Depends(get_comment_service)):
    return service.get_comment_by_id(comment_id)

@router.get('/by_task/', response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
def get_comments_by_task(
    task_id: int = Query(..., description='id задачи'),
    service: CommentService = Depends(get_comment_service)
):
    return service.get_comments_by_task(task_id)

@router.get('/by_author/', response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
def get_comment_by_author(
    author_id: int = Query(..., description='id пользователя'),
    service: CommentService = Depends(get_comment_service)
):
    return service.get_comments_by_author(author_id)

@router.post('', response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(comment_data: CommentCreate, service: CommentService = Depends(get_comment_service)):
    return service.create_comment(comment_data)

@router.put('/{comment_id}', response_model=CommentResponse, status_code=status.HTTP_200_OK)
def update_comment(comment_id: int, comment_data: CommentUpdate, service: CommentService = Depends(get_comment_service)):
    return service.update_comment(comment_id, comment_data)

@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, service: CommentService = Depends(get_comment_service)):
    return service.delete_comment(comment_id)
