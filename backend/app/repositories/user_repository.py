from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import User
from ..schemas.user import UserCreate
from ..schemas.task import TaskResponse
from .base import BaseRepository
from ..security import hash_password

class UserRepository(BaseRepository[User]):
    def __init__(self, db:Session):
        super().__init__(db, User)


    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
