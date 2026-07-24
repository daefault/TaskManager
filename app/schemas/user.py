from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description='Юзернейм пользователя(не больше 50 символов)')
    email: EmailStr = Field(..., min_length=3, max_length=100, description='Эл. почта пользователя (не длиннее 100 символов)')
    password: str = Field(..., min_length=6)
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)

class UserResponse(BaseModel): 
    id: int 
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserBriefResponse(BaseModel):
    id: int
    username: str
    
    model_config = ConfigDict(from_attributes=True)