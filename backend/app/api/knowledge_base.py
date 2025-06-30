"""
知识库管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()
security = HTTPBearer()

@router.get("/")
async def get_knowledge_bases(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取用户的知识库
    knowledge_bases = kb_service.get_user_knowledge_bases(current_user.id)
    return knowledge_bases

@router.post("/")
async def create_knowledge_base(
    name: str,
    description: Optional[str] = None,
    kb_type: str = "text",
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """创建知识库"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 创建知识库
    knowledge_base = kb_service.create_knowledge_base(
        name=name,
        description=description,
        kb_type=kb_type,
        owner_id=current_user.id
    )
    
    return knowledge_base

@router.get("/{kb_id}")
async def get_knowledge_base(
    kb_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取知识库详情"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取知识库
    knowledge_base = kb_service.get_knowledge_base_by_id(kb_id, current_user.id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在或无权限访问"
        )
    
    return knowledge_base

@router.get("/{kb_id}/chunks")
async def get_knowledge_base_chunks(
    kb_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取知识库文本分块"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取知识库分块
    chunks = kb_service.get_knowledge_base_chunks(kb_id, current_user.id)
    return chunks

@router.get("/{kb_id}/images")
async def get_knowledge_base_images(
    kb_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取知识库图片"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取知识库图片
    images = kb_service.get_knowledge_base_images(kb_id, current_user.id)
    return images

@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """删除知识库"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 删除知识库
    success = kb_service.delete_knowledge_base(kb_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在或无权限删除"
        )
    
    return {"message": "知识库删除成功"}

@router.post("/{kb_id}/upload-doc")
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """上传文档到知识库"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 上传文档
    result = await kb_service.upload_document(
        kb_id=kb_id,
        file=file,
        user_id=current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result

@router.post("/{kb_id}/upload-image")
async def upload_image(
    kb_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """上传图片到知识库"""
    auth_service = AuthService(db)
    kb_service = KnowledgeBaseService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 上传图片
    result = await kb_service.upload_image(
        kb_id=kb_id,
        file=file,
        description=description,
        user_id=current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return result 