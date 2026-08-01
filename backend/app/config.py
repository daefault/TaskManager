from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / '.env'
load_dotenv()

class Settings(BaseSettings):
    app_name: str = 'TaskManager'
    database_url: str = os.getenv('DATABASE_URL','postgresql://postgres:postgres@db:5432/fastapi_db')
    cors_origins: list = []
    static_dir: str = 'static'
    images_dir: str = 'images'

    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    class Config: 
        env_file = '.env'

settings = Settings()