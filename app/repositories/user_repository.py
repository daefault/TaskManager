from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.user import User
from ..schemas.user import UserCreate
from .base import BaseRepository
import bcrypt


def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


class UserRepository(BaseRepository[User]):
    def __init__(self, db:Session):
        super().__init__(db, User)

    def create(self, data: UserCreate) -> User:
        hashed_password = hash_password(data.password)
        user_data = data.model_dump()
        user_data['password'] = hashed_password
        return super().create(user_data)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
        