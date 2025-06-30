"""
用户管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()

@router.get("/")
async def get_users(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取用户列表（仅管理员）"""
    auth_service = AuthService(db)
    user_service = UserService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 检查权限
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    users = user_service.get_all_users()
    return users

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取用户信息"""
    auth_service = AuthService(db)
    user_service = UserService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 检查权限（只能查看自己的信息或管理员可以查看所有）
    if str(current_user.id) != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user 