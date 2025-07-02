"""
文件访问API
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from typing import Optional
from app.core.config import settings
from app.core.database import get_db
from app.models.knowledge_base import ImageVector
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{filename}")
async def get_file(
    filename: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    获取文件内容
    
    Args:
        filename: 文件名
        db: 数据库会话
        current_user: 当前用户（可选，支持匿名访问）
    
    Returns:
        FileResponse: 文件内容
    """
    try:
        # 安全检查：防止路径遍历攻击
        if ".." in filename or "/" in filename or "\\" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # 构建文件路径
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # 检查文件是否为图片
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # 如果用户已登录，可以添加额外的权限检查
        if current_user:
            # 检查用户是否有权限访问该文件
            # 这里可以根据业务需求添加更复杂的权限逻辑
            pass
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=f"image/{file_ext[1:]}" if file_ext != '.jpg' else "image/jpeg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/image/{image_id}")
async def get_image_by_id(
    image_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    根据图片ID获取图片文件
    
    Args:
        image_id: 图片ID
        db: 数据库会话
        current_user: 当前用户（可选）
    
    Returns:
        FileResponse: 图片文件
    """
    try:
        # 从数据库查询图片信息
        image = db.query(ImageVector).filter(ImageVector.id == image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # 调用文件访问接口
        return await get_file(image.filename, db, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
