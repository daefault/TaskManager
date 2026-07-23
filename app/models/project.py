from sqlalchemy import Column, Integer, String, Enum, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum

class Status(enum.Enum):
    ACTIVE='active'
    ARCHIVED = 'archived'


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    status = Column(Enum(Status), nullable=False, default=Status.ACTIVE)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship('User', back_populates='project')