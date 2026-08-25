import pytest 
from fastapi.testclient import TestClient
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
from unittest.mock import patch


env_path = Path(__file__).parent.parent / '.env.test'
load_dotenv(env_path)

TEST_DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


from app.main import app
from app.database import Base, get_db
@pytest.fixture(scope='function')
def db_session():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try: 
        yield db
    finally: 
        db.rollback()
        db.close()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try: 
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)

#Заглушка для Celery во время тестов
@pytest.fixture(autouse=True)
def mock_celery_tasks():
    with patch('app.tasks.send_task_assigned_notification.delay') as mock:
        yield mock