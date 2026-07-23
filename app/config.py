from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = 'TaskManager'
    database_url: str = 'postgresql://postgres:postgres@db:5432/fastapi_db'
    cors_origins: list = []
    static_dir: str = 'static'
    images_dir: str = 'images'
    class Config: 
        env_file = '.env'

settings = Settings()