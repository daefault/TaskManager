from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Notification
from .base import BaseRepository
from datetime import datetime, timedelta


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db:Session):
        super().__init__(db, Notification)

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100, is_read: Optional[bool] = None) -> List[Notification]:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)

        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_user_count(self, user_id: int, is_read: Optional[bool] = None) -> int:
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)

        return query.count()

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        notification = self.get_by_id(notification_id)
        if not notification:
            return

        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def mark_all_as_read(self, user_id: int) -> int:
        unread = self.db.query(Notification).filter(Notification.user_id == user_id, Notification.is_read == False).all()
        count = len(unread)
        for notification in unread:
            notification.is_read = True
        self.db.commit()
        return count

    def delete_old_notification_for_user(self, user_id: int, days: int = 30) -> int:
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.db.query(Notification).filter(
            Notification.created_at < cutoff, 
            Notification.user_id == user_id).delete(synchronize_session=False)
        self.db.commit()

    def bulk_mark_as_read(self, user_id: int, notifications_ids: List[int]) -> int:
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.id.in_(notifications_ids),
            Notification.is_read == False 
            ).update({'is_read': True}, synchronize_session=False)
        self.db.commit()
        return count

    def bulk_delete(self, user_id: int, notification_ids: List[int]) -> int:
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id, 
            Notification.id.in_(notification_ids)
        ).delete(synchronize_session=False)
        self.db.commit()
        return count       

    def delete_all_read(self, user_id: int) -> int:
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).delete(synchronize_session=False)
        self.db.commit()
        return count