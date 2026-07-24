from sqlalchemy import Column, Integer, String, Enum, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from ..enums import TaskStatus, Priority 
from .association import task_assignees

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), unique=True, nullable=False)
    description = Column(Text)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    priority = Column(Enum(Priority), nullable=False, default=Priority.LOW)
    deadline = Column(DateTime)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), index=True)
    creator_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship('Project', back_populates='tasks')

    creator = relationship('User', foreign_keys=[creator_id], back_populates='created_tasks')

    assignees = relationship(
        'User',
        secondary=task_assignees,
        back_populates = 'assigned_tasks',
        lazy='selectin'
    )

    comments = relationship('Comment', back_populates='task', cascade='all, delete-orphan')