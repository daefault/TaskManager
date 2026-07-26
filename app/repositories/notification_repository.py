from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Notification
from .base import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db:Session):
        super().__init__(db, Notification)

