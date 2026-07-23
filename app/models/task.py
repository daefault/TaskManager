from sqlalchemy import Column, Integer, String, Enum, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class Status(enum.Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'
    CANCELLED = 'cancelled'

class Priority(enum.Enum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    status = Column(Enum(Status), nullable=False, default=Status.PENDING)
    priority = Column(Enum(Priority), nullable=False, default=Priority.LOW)
    deadline = Column(DateTime)
    project_id = Column(Integer, ForeignKey('projects.id'), index=True)
    creator_id = Column(Integer, ForeignKey('users.id'), index=True)
    assignee_id = Column(Integer, ForeignKey('users.id'), index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    