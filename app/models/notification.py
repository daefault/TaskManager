from sqlalchemy import Column, Integer, String, Enum, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class Type(enum.Enum):
    TASK_ASSIGNED = 'task_assigned'
    STATUS_CHANGED = 'status_changed'
    DEADLINE_REMINDER = 'deadline_reminder'

class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    type = Column(Enum(Type), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)