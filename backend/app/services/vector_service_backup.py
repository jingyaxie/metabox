"""
向量化服务 - 使用Chroma向量数据库
"""
import asyncio
import aiohttp
import numpy as np
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
import os
from app.core.config import settings
from app.models.knowledge_base import TextChunk, ImageVector
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class VectorService:
    """向量化服务类 - 使用Chroma"""
    
    def __init__(self, db: Session):
        self.db = db
        # 初始化Chroma客户端
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        self._init_collections()
    
    def _init_collections(self):
        """初始化向量集合"""
        try:
            # 文本向量集合
            self.chroma_client.get_collection("text_vectors")
        except:
            self.chroma_client.create_collection(
                name="text_vectors",
                metadata={
                    "description": "Text vectors for knowledge base",
                    "dimension": settings.TEXT_EMBEDDING_DIMENSION
                }
            )
        
        try:
            # 图片内容集合（存储OCR文字和描述）
            self.chroma_client.get_collection("image_content")
        except:
            self.chroma_client.create_collection(
                name="image_content",
                metadata={
                    "description": "Image content (OCR text and descriptions)",
                    "dimension": settings.TEXT_EMBEDDING_DIMENSION
                }
            )
    
    async def get_text_embedding(self, text: str) -> List[float]:
        """获取文本向量"""
        if not settings.OPENAI_API_KEY:
            # 使用简单的TF-IDF作为fallback
            return self._simple_text_embedding(text)
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "input": text,
                    "model": settings.TEXT_EMBEDDING_MODEL
                }
                
                async with session.post(
                    f"{settings.OPENAI_BASE_URL}/embeddings",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["data"][0]["embedding"]
                    else:
                        logger.warning(f"OpenAI embedding failed: {response.status}")
                        return self._simple_text_embedding(text)
        except Exception as e:
            logger.error(f"Text embedding error: {e}")
            return self._simple_text_embedding(text)
    
    def _simple_text_embedding(self, text: str) -> List[float]:
        """简单的文本向量化（fallback）"""
        # 简单的字符频率向量化
        import string
        base_dim = 128
        vector = [0.0] * base_dim
        for char in text.lower():
            if char in string.ascii_lowercase:
                vector[ord(char) - ord('a')] += 1.0
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        # 补零到目标维度
        target_dim = settings.TEXT_EMBEDDING_DIMENSION
        if len(vector) < target_dim:
            vector += [0.0] * (target_dim - len(vector))
        else:
            vector = vector[:target_dim]
        return vector[:settings.TEXT_EMBEDDING_DIMENSION]
    
    async def analyze_image_content(self, image_path: str) -> Dict[str, str]:
        """分析图片内容（OCR + 描述）"""
        try:
            from PIL import Image
            import base64
            import io
            
            # 读取图片
            image = Image.open(image_path)
            
            # 调整图片大小
            max_size = settings.IMAGE_MAX_SIZE
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # 转换为base64
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=settings.IMAGE_QUALITY)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            
            # 调用大模型进行OCR
            ocr_text = await self._call_model_ocr(img_base64)
            
            # 调用大模型进行图片描述
            description = await self._call_model_vision(img_base64)
            
            return {
                "ocr_text": ocr_text or "",
                "description": description or "",
                "combined_text": f"{ocr_text or ''} {description or ''}".strip()
            }
            
        except Exception as e:
            logger.error(f"Image content analysis error: {e}")
            return {
                "ocr_text": "",
                "description": "",
                "combined_text": ""
            }
    
    async def _call_model_ocr(self, image_base64: str) -> Optional[str]:
        """调用大模型进行OCR"""
        if not settings.OPENAI_API_KEY:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": settings.IMAGE_OCR_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "请识别这张图片中的所有文字内容，包括标题、正文、标签等所有可见文字。保持原有的格式和顺序。如果图片中没有文字，请返回'无文字内容'。只返回识别出的文字，不要添加其他描述。"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.1
                }
                
                async with session.post(
                    f"{settings.OPENAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"].strip()
                    else:
                        logger.warning(f"OCR API call failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"OCR API error: {e}")
            return None
    
    async def _call_model_vision(self, image_base64: str) -> Optional[str]:
        """调用大模型进行图片描述"""
        if not settings.OPENAI_API_KEY:
            return None
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": settings.IMAGE_VISION_MODEL,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "请详细描述这张图片的内容，包括图片中的主要物体、人物、场景、颜色、风格、构图等视觉特征，以及图片的整体氛围和情感。如果是图表或文档，请描述其结构和内容。用中文描述，语言要准确、详细。"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 500,
                    "temperature": 0.3
                }
                
                async with session.post(
                    f"{settings.OPENAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"].strip()
                    else:
                        logger.warning(f"Vision API call failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Vision API error: {e}")
            return None
    
    async def vectorize_text_chunk(self, chunk: TextChunk) -> bool:
        """向量化文本分块"""
        try:
            # 获取向量
            vector = await self.get_text_embedding(chunk.content)
            
            # 存储到Chroma
            collection = self.chroma_client.get_collection("text_vectors")
            collection.upsert(
                ids=[str(chunk.id)],
                embeddings=[vector],
                documents=[chunk.content],
                metadatas=[{
                    "source_file": chunk.source_file,
                    "chunk_index": chunk.chunk_index,
                    "knowledge_base_id": str(chunk.knowledge_base_id),
                    "created_at": chunk.created_at.isoformat()
                }]
            )
            
            return True
        except Exception as e:
            logger.error(f"Vectorize text chunk error: {e}")
            return False
    
    async def vectorize_image(self, image: ImageVector) -> bool:
        """向量化图片（分析内容并存储）"""
        try:
            # 分析图片内容
            image_path = os.path.join(settings.UPLOAD_DIR, image.filename)
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return False
            
            content_analysis = await self.analyze_image_content(image_path)
            
            # 获取组合文本的向量
            combined_text = content_analysis["combined_text"]
            if not combined_text:
                logger.warning(f"No content extracted from image: {image.filename}")
                return False
            
            vector = await self.get_text_embedding(combined_text)
            
            # 生成图片访问链接
            image_url = f"/api/v1/files/{image.filename}"
            
            # 存储到Chroma
            collection = self.chroma_client.get_collection("image_content")
            collection.upsert(
                ids=[str(image.id)],
                embeddings=[vector],
                documents=[combined_text],
                metadatas=[{
                    "filename": image.filename,
                    "image_url": image_url,
                    "ocr_text": content_analysis["ocr_text"],
                    "description": content_analysis["description"],
                    "knowledge_base_id": str(image.knowledge_base_id),
                    "created_at": image.created_at.isoformat()
                }]
            )
            
            # 更新数据库中的描述
            image.description = content_analysis["description"]
            self.db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Vectorize image error: {e}")
            return False
    
    async def search_text(self, query: str, kb_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """文本向量搜索"""
        try:
            # 获取查询向量
            query_vector = await self.get_text_embedding(query)
            
            # 构建过滤条件
            where_filter = None
            if kb_ids:
                where_filter = {"knowledge_base_id": {"$in": kb_ids}}
            
            # 搜索
            collection = self.chroma_client.get_collection("text_vectors")
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=where_filter,
                include=["metadatas", "documents", "distances"]
            )
            
            # 格式化结果
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "score": 1.0 - results["distances"][0][i],  # 转换为相似度
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search text error: {e}")
            return []
    
    async def search_image(self, query: str, kb_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """图片内容搜索"""
        try:
            # 获取查询向量
            query_vector = await self.get_text_embedding(query)
            
            # 构建过滤条件
            where_filter = None
            if kb_ids:
                where_filter = {"knowledge_base_id": {"$in": kb_ids}}
            
            # 搜索
            collection = self.chroma_client.get_collection("image_content")
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=where_filter,
                include=["metadatas", "documents", "distances"]
            )
            
            # 格式化结果
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "score": 1.0 - results["distances"][0][i],  # 转换为相似度
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search image error: {e}")
            return []
    
    async def hybrid_search(self, query: str, kb_ids: List[str], top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """混合搜索（文本 + 图片内容）"""
        try:
            # 并行搜索文本和图片
            text_task = self.search_text(query, kb_ids, top_k)
            image_task = self.search_image(query, kb_ids, top_k)
            
            text_results, image_results = await asyncio.gather(text_task, image_task)
            
            return {
                "text_results": text_results,
                "image_results": image_results
            }
            
        except Exception as e:
            logger.error(f"Hybrid search error: {e}")
            return {
                "text_results": [],
                "image_results": []
            } 