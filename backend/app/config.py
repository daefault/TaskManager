from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv()

class Settings(BaseSettings):
    app_name: str = 'TaskManager'
    database_url: str = os.getenv('DATABASE_URL','postgresql://postgres:postgres@db:5432/fastapi_db')
    redis_url: str = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    celery_broker_url: str = os.getenv('CELERY_BROKER_URL','redis://redis:6379/0')
    celery_result_backend: str = os.getenv('CELERY_RESULT_BACKEND','redis://redis:6379/0')



    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MAX_PROJECTS_PER_USER: int = 100
    MAX_TASKS_PER_PROJECT: int = 500
    MAX_TASKS_PER_USER: int = 1000
    MAX_COMMENTS_PER_USER: int = 10000
    MAX_NOTIFICATIONS_PER_USER: int = 1000
    DAYS_TO_DELETE_NOTIFICATIONS: int = 30
    
    model_config = ConfigDict(
        env_file = '.env',
        extra = 'ignore'
    )
       

settings = Settings()