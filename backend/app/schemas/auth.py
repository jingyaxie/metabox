"""
认证相关的数据模式
"""
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str

class UserRegister(BaseModel):
    """用户注册请求"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str
    user_id: str
    username: str
    role: str

class UserProfile(BaseModel):
    """用户信息模型"""
    username: str
    email: EmailStr

class PasswordChange(BaseModel):
    """密码修改模型"""
    current_password: str
    new_password: str 