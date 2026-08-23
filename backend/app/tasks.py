from celery import shared_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.notification_service import NotificationService
from app.repositories import NotificationRepository
from app.repositories import UserRepository, TaskRepository


@shared_task
def send_task_assigned_notification(user_id: int, task_title: str, task_id: int) -> dict:
    db: Session = SessionLocal()
    try:
        notification_repository = NotificationRepository(db)
        user_repository = UserRepository(db)
        notification_service = NotificationService(notification_repository, user_repository)
        notification_service.notify_task_assigned(
            user_id=user_id,
            task_title=task_title,
            task_id=task_id
        )
        return {'status': 'success', 'user_id': user_id, 'task_id': task_id}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
    finally:
        db.close()
        
@shared_task
def send_user_inactive_reminder(user_id: int) -> dict:
    db: Session = SessionLocal()
    try: 
        notification_repository = NotificationRepository(db)
        user_repository = UserRepository(db)
        notification_service = NotificationService(notification_repository, user_repository)
        notification_service.notify_deadline_reminder(
            user_id=user_id
        )
        return {'status': 'success', 'user_id': user_id}
    except Exception as e:
        return {'status': 'error', 'error': str(e)}
    finally:
        db.close()

@shared_task
def check_overdue_tasks() -> dict:
    db: Session = SessionLocal()
    try:
        task_repository = TaskRepository(db)
        tasks = task_repository.check_overdue_task()
        return {
            'status': 'success',
            'task_ids': [t.id for t in tasks]
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': e
        }
    finally:
        db.close()
    