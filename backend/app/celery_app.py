from celery import Celery
from .config import settings


celery_app = Celery(
    'task_manager',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['app.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Yekaterinburg',
    enable_utc=True
)

celery_app.conf.beat_schedule = {
    'check-overdue-tasks': {
        "task": "app.tasks.check_overdue_tasks",
        "schedule": 300.0,
        "args":()
    }
}

if __name__ == '__main__':
    celery_app.start()