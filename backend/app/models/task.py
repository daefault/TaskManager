from sqlalchemy import String, Enum, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from ..database import Base
from ..enums import TaskStatus, Priority 
from .association import task_assignees
from datetime import datetime
from typing import Optional



class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), nullable=False, default=TaskStatus.PENDING)
    priority: Mapped[Priority] = mapped_column(Enum(Priority), nullable=False, default=Priority.LOW)
    deadline: Mapped[Optional[datetime]] = mapped_column(DateTime)
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), index=True, nullable=False)
    creator_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('project_id', 'title', name='uq_task_title_per_project'),
    )

    project: Mapped['Project'] = relationship('Project', back_populates='tasks')

    creator: Mapped['User'] = relationship('User', foreign_keys=[creator_id], back_populates='created_tasks')

    assignees: Mapped[list['User']] = relationship(
        'User',
        secondary=task_assignees,
        back_populates = 'assigneed_tasks',
        lazy='selectin'
    )

    comments: Mapped[list['Comment']] = relationship('Comment', back_populates='task', cascade='all, delete-orphan')