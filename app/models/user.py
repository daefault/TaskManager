from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base
from sqlalchemy.orm import relationship
from .association import task_assignees

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    project = relationship('Project', back_populates='owner', cascade='all, delete-orphan')
    created_tasks = relationship('Task', foreign_keys='Task.creator_id', back_populates='creator')
    assigneed_tasks = relationship(
        'Task',
        secondary=task_assignees,
        back_populates='assignees',
        lazy='selectin'
    )
    comments = relationship('Comment', back_populates='author')
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')