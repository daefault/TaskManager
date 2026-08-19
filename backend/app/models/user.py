from sqlalchemy import String, DateTime
from sqlalchemy.sql import func
from ..database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .association import task_assignees, project_members
from datetime import datetime
from typing import Optional


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    projects: Mapped[list['Project']] = relationship('Project', back_populates='owner', cascade='all, delete-orphan')
    created_tasks: Mapped[list['Task']] = relationship('Task', foreign_keys='Task.creator_id', back_populates='creator')
    assigneed_tasks: Mapped[list['Task']] = relationship(
        'Task',
        secondary=task_assignees,
        back_populates='assignees',
        lazy='selectin'
    )
    comments: Mapped[list['Comment']] = relationship('Comment', back_populates='author')
    notifications: Mapped[list['Notification']] = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    project_member: Mapped[list['Project']] = relationship(
        'Project',
        secondary=project_members,
        back_populates='members',
        lazy='selectin'
    )