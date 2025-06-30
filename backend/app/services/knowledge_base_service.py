"""
知识库服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import UploadFile
import uuid
import os
from datetime import datetime

from app.models.knowledge_base import KnowledgeBase, TextChunk, ImageVector
from app.core.config import settings

class KnowledgeBaseService:
    """知识库服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_knowledge_bases(self, user_id: str) -> List[KnowledgeBase]:
        """获取用户的知识库列表"""
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.owner_id == user_id
        ).all()
    
    def get_knowledge_base_by_id(self, kb_id: str, user_id: str) -> Optional[KnowledgeBase]:
        """根据ID获取知识库（检查权限）"""
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.owner_id == user_id
        ).first()
    
    def create_knowledge_base(
        self, 
        name: str, 
        description: Optional[str], 
        kb_type: str, 
        owner_id: str
    ) -> KnowledgeBase:
        """创建知识库"""
        collection_name = f"kb_{uuid.uuid4().hex}"
        
        knowledge_base = KnowledgeBase(
            name=name,
            description=description,
            type=kb_type,
            owner_id=owner_id,
            vector_collection_name=collection_name
        )
        
        self.db.add(knowledge_base)
        self.db.commit()
        self.db.refresh(knowledge_base)
        
        return knowledge_base
    
    def delete_knowledge_base(self, kb_id: str, user_id: str) -> bool:
        """删除知识库"""
        knowledge_base = self.get_knowledge_base_by_id(kb_id, user_id)
        if not knowledge_base:
            return False
        
        self.db.delete(knowledge_base)
        self.db.commit()
        return True
    
    async def upload_document(
        self, 
        kb_id: str, 
        file: UploadFile, 
        user_id: str
    ) -> Dict[str, Any]:
        """上传文档到知识库"""
        try:
            # 检查知识库权限
            knowledge_base = self.get_knowledge_base_by_id(kb_id, user_id)
            if not knowledge_base:
                return {
                    "success": False,
                    "message": "知识库不存在或无权限访问"
                }
            
            # 检查文件类型
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension not in settings.ALLOWED_EXTENSIONS:
                return {
                    "success": False,
                    "message": f"不支持的文件类型: {file_extension}"
                }
            
            # 保存文件
            file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # TODO: 实现文档解析和向量化
            # 这里应该调用文档解析服务
            
            return {
                "success": True,
                "message": "文档上传成功",
                "file_path": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"上传失败: {str(e)}"
            }
    
    async def upload_image(
        self, 
        kb_id: str, 
        file: UploadFile, 
        description: Optional[str], 
        user_id: str
    ) -> Dict[str, Any]:
        """上传图片到知识库"""
        try:
            # 检查知识库权限
            knowledge_base = self.get_knowledge_base_by_id(kb_id, user_id)
            if not knowledge_base:
                return {
                    "success": False,
                    "message": "知识库不存在或无权限访问"
                }
            
            # 检查文件类型
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png', 'gif']:
                return {
                    "success": False,
                    "message": f"不支持的图片格式: {file_extension}"
                }
            
            # 保存文件
            file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # 创建图片向量记录
            image_vector = ImageVector(
                knowledge_base_id=kb_id,
                filename=file.filename,
                file_path=file_path,
                description=description,
                file_size=len(content),
                mime_type=file.content_type
            )
            
            self.db.add(image_vector)
            self.db.commit()
            
            # TODO: 实现图片向量化
            # 这里应该调用图片向量化服务
            
            return {
                "success": True,
                "message": "图片上传成功",
                "file_path": file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"上传失败: {str(e)}"
            } 