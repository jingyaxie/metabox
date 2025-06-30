"""
认证 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, TokenResponse, UserProfile, PasswordChange
from app.services.auth_service import AuthService

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册"""
    auth_service = AuthService(db)
    
    # 检查用户名是否已存在
    if auth_service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if auth_service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    user = auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    # 生成访问令牌
    access_token = auth_service.create_access_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id),
        username=user.username,
        role=user.role
    )

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    auth_service = AuthService(db)
    
    # 验证用户凭据
    user = auth_service.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()
    
    # 生成访问令牌
    access_token = auth_service.create_access_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=str(user.id),
        username=user.username,
        role=user.role
    )

@router.get("/me")
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前用户信息"""
    auth_service = AuthService(db)
    
    try:
        user = auth_service.get_current_user(credentials.credentials)
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )

@router.post("/refresh")
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    auth_service = AuthService(db)
    
    try:
        user = auth_service.get_current_user(credentials.credentials)
        new_token = auth_service.create_access_token(user.id)
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            user_id=str(user.id),
            username=user.username,
            role=user.role
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌"
        )

@router.get("/profile")
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    auth_service = AuthService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }

@router.put("/profile")
async def update_profile(
    profile_data: UserProfile,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """更新用户信息"""
    auth_service = AuthService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 检查用户名是否已被其他用户使用
    existing_user = auth_service.get_user_by_username(profile_data.username)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )
    
    # 检查邮箱是否已被其他用户使用
    existing_user = auth_service.get_user_by_email(profile_data.email)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被使用"
        )
    
    # 更新用户信息
    auth_service.update_user_profile(
        user_id=current_user.id,
        username=profile_data.username,
        email=profile_data.email
    )
    
    return {"message": "个人信息更新成功"}

@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """修改密码"""
    auth_service = AuthService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 验证当前密码
    if not auth_service.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新密码
    auth_service.update_user_password(current_user.id, password_data.new_password)
    
    return {"message": "密码修改成功"}

@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """用户登出"""
    # 这里可以添加令牌黑名单逻辑
    return {"message": "登出成功"} 