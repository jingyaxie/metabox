"""
知识库服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from fastapi import UploadFile
import uuid
import os
from datetime import datetime
import asyncio

from app.models.knowledge_base import KnowledgeBase, TextChunk, ImageVector
from app.core.config import settings
from app.services.vector_service import VectorService

class KnowledgeBaseService:
    """知识库服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_service = VectorService(db)
    
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
    
    def create_knowledge_base(self, user_id: str, name: str, description: str = "") -> KnowledgeBase:
        """创建知识库"""
        knowledge_base = KnowledgeBase(
            name=name,
            description=description,
            owner_id=user_id
        )
        self.db.add(knowledge_base)
        self.db.commit()
        self.db.refresh(knowledge_base)
        return knowledge_base
    
    def update_knowledge_base(self, kb_id: str, user_id: str, name: str, description: str) -> Optional[KnowledgeBase]:
        """更新知识库"""
        knowledge_base = self.get_knowledge_base_by_id(kb_id, user_id)
        if not knowledge_base:
            return None
        
        knowledge_base.name = name
        knowledge_base.description = description
        knowledge_base.updated_at = datetime.utcnow()
        
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
            
            # 创建文本分块
            chunks = self._create_text_chunks(content.decode('utf-8', errors='ignore'), file.filename)
            created_chunks = []
            
            for i, chunk_content in enumerate(chunks):
                text_chunk = TextChunk(
                    knowledge_base_id=kb_id,
                    content=chunk_content,
                    source_file=file.filename,
                    chunk_index=i
                )
                self.db.add(text_chunk)
                created_chunks.append(text_chunk)
            
            self.db.commit()
            
            # 异步向量化所有分块
            vectorization_tasks = []
            for chunk in created_chunks:
                task = self.vector_service.vectorize_text_chunk(chunk)
                vectorization_tasks.append(task)
            
            # 等待所有向量化任务完成
            if vectorization_tasks:
                await asyncio.gather(*vectorization_tasks, return_exceptions=True)
            
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
        description: str, 
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
            
            # 创建图片记录
            image_vector = ImageVector(
                knowledge_base_id=kb_id,
                filename=file.filename,
                description=description,
                file_path=file_path
            )
            self.db.add(image_vector)
            self.db.commit()
            self.db.refresh(image_vector)
            
            # 异步向量化图片
            await self.vector_service.vectorize_image(image_vector)
            
            return {
                "success": True,
                "message": "图片上传成功",
                "file_path": file_path,
                "image_id": str(image_vector.id)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"上传失败: {str(e)}"
            }
    
    def _create_text_chunks(self, text: str, filename: str) -> List[str]:
        """创建文本分块（改进版）"""
        # 按段落分割
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # 如果当前块加上新段落超过限制，保存当前块
            if len(current_chunk) + len(paragraph) > settings.CHUNK_SIZE:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # 保存最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # 如果没有分块，将整个文本作为一个块
        if not chunks:
            chunks = [text]
        
        # 应用重叠策略
        if len(chunks) > 1 and settings.CHUNK_OVERLAP > 0:
            overlapped_chunks = []
            for i, chunk in enumerate(chunks):
                if i > 0:
                    # 添加前一个块的结尾作为重叠
                    prev_chunk = chunks[i-1]
                    overlap_text = prev_chunk[-settings.CHUNK_OVERLAP:]
                    chunk = overlap_text + "\n\n" + chunk
                overlapped_chunks.append(chunk)
            chunks = overlapped_chunks
        
        return chunks 