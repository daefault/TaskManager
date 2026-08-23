from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import User
from ..schemas.user import UserCreate
from ..schemas.task import TaskResponse
from .base import BaseRepository
from ..security import hash_password
from datetime import datetime, timedelta

class UserRepository(BaseRepository[User]):
    def __init__(self, db:Session):
        super().__init__(db, User)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def soft_delete(self, user_id: int) -> None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user: 
            return False
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)

    def exists(self, user_id: int) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return False
        return True

    def is_user_inactive(self, user_id: int) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.is_active:
            return False
        return True
    
    def restore_user(self, user_id: int) -> Optional[User]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user: 
            return False
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user_activity(self, user_id: int) -> Optional[User]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if user.last_activity_at is None or (datetime.now() - user.last_activity_at) > timedelta(minutes=5):
            user.last_activity_at = datetime.now()
            self.db.commit()
            self.db.refresh(user)
        return user

    def search_users(self, query: str, limit: int = 10) -> List[User]:
        return self.db.query(User).filter(
            (User.username.ilike(f"%{query}%")) | 
            (User.email.ilike(f"%{query}%")),
            (User.is_active == True)
        ).limit(limit).all()