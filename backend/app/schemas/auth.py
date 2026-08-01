from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description='Имя пользователя (только буквы и цифры)')
    email: EmailStr = Field(..., description='email адрес')
    password: str = Field(..., min_length=6, max_length=100, description='Пароль (минимум 6 символов)')

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('Имя пользователя должно содержать только буквы и цифры')
        return v

class UserLogin(BaseModel):
    username: str = Field(..., description='Имя пользователя')
    password: str = Field(..., description='Пароль')

class TokenResponse(BaseModel):
    access_token: str = Field(..., description='JWT токен доступа (30 минут)')
    refresh_token: str = Field(..., description='JWT токен обновления (7 дней)')
    token_type: str = Field(default='bearer', description='Тип токена')

class TokenRefresh(BaseModel): 
    refresh_token: str = Field(..., description='Refresh токен для получения нового access токена')

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False

    class Config: 
        from_attributes = True