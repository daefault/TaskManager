from .config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import logging

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

logger.info('Database connected | url = %s', settings.database_url)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error('Database error %s', str(e), exc_info=True)
    finally:
        db.close()
