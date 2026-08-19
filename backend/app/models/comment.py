from sqlalchemy import String, Enum, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from ..database import Base
from typing import Optional
from datetime import datetime


class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), index=True, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    task: Mapped['Task'] = relationship('Task', back_populates='comments')
    author: Mapped['User'] = relationship('User', back_populates='comments')