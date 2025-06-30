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
    
    def get_knowledge_base_chunks(self, kb_id: str, user_id: str) -> List[TextChunk]:
        """获取知识库的文本分块"""
        # 先检查权限
        kb = self.get_knowledge_base_by_id(kb_id, user_id)
        if not kb:
            return []
        
        return self.db.query(TextChunk).filter(
            TextChunk.knowledge_base_id == kb_id
        ).order_by(TextChunk.chunk_index).all()
    
    def get_knowledge_base_images(self, kb_id: str, user_id: str) -> List[ImageVector]:
        """获取知识库的图片"""
        # 先检查权限
        kb = self.get_knowledge_base_by_id(kb_id, user_id)
        if not kb:
            return []
        
        return self.db.query(ImageVector).filter(
            ImageVector.knowledge_base_id == kb_id
        ).order_by(ImageVector.created_at.desc()).all()
    
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
            
            # 创建文本分块（模拟）
            chunks = self._create_text_chunks(content.decode('utf-8', errors='ignore'), file.filename)
            for i, chunk_content in enumerate(chunks):
                text_chunk = TextChunk(
                    knowledge_base_id=kb_id,
                    content=chunk_content,
                    source_file=file.filename,
                    chunk_index=i
                )
                self.db.add(text_chunk)
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "文档上传成功",
                "file_path": file_path,
                "chunks_count": len(chunks)
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
    
    def _create_text_chunks(self, text: str, filename: str) -> List[str]:
        """创建文本分块（简单实现）"""
        # 简单的文本分块，按段落分割
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) > 1000:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks if chunks else [text] 