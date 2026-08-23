from sqlalchemy import  String, Enum, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from ..database import Base
from ..enums import Status
from .association import project_members
from datetime import datetime
from typing import Optional


class Project(Base):
    __tablename__ = 'projects'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False, default=Status.ACTIVE)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint('owner_id', 'name', name='uq_project_name_per_user'),
    )

    owner: Mapped['User'] = relationship('User', back_populates='projects')
    tasks: Mapped[list['Task']] = relationship('Task', back_populates='project', cascade='all, delete-orphan')

    members: Mapped[list['User']] = relationship(
        'User',
        secondary=project_members,
        back_populates='project_member',
        lazy='selectin'
    )