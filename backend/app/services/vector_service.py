"""
向量化服务
"""
import asyncio
import aiohttp
import numpy as np
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging
from app.core.config import settings
from app.models.knowledge_base import TextChunk, ImageVector
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)

class VectorService:
    """向量化服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.qdrant_client = qdrant_client.QdrantClient(settings.QDRANT_URL)
        self._init_collections()
    
    def _init_collections(self):
        """初始化向量集合"""
        try:
            # 文本向量集合
            self.qdrant_client.get_collection("text_vectors")
        except:
            self.qdrant_client.create_collection(
                collection_name="text_vectors",
                vectors_config=VectorParams(
                    size=settings.TEXT_EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
            )
        
        try:
            # 图片向量集合
            self.qdrant_client.get_collection("image_vectors")
        except:
            self.qdrant_client.create_collection(
                collection_name="image_vectors",
                vectors_config=VectorParams(
                    size=settings.IMAGE_EMBEDDING_DIMENSION,
                    distance=Distance.COSINE
                )
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
    
    async def get_image_embedding(self, image_path: str) -> List[float]:
        """获取图片向量"""
        try:
            # 这里应该集成CLIP或其他图片向量化模型
            # 暂时使用随机向量作为placeholder
            import random
            random.seed(hash(image_path))
            vector = [random.uniform(-1, 1) for _ in range(settings.IMAGE_EMBEDDING_DIMENSION)]
            # 归一化
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = [v / norm for v in vector]
            return vector
        except Exception as e:
            logger.error(f"Image embedding error: {e}")
            return [0.0] * settings.IMAGE_EMBEDDING_DIMENSION
    
    async def vectorize_text_chunk(self, chunk: TextChunk) -> bool:
        """向量化文本分块"""
        try:
            # 获取向量
            vector = await self.get_text_embedding(chunk.content)
            
            # 存储到Qdrant
            point = PointStruct(
                id=str(chunk.id),
                vector=vector,
                payload={
                    "content": chunk.content,
                    "source_file": chunk.source_file,
                    "chunk_index": chunk.chunk_index,
                    "knowledge_base_id": str(chunk.knowledge_base_id),
                    "created_at": chunk.created_at.isoformat()
                }
            )
            
            self.qdrant_client.upsert(
                collection_name="text_vectors",
                points=[point]
            )
            
            return True
        except Exception as e:
            logger.error(f"Vectorize text chunk error: {e}")
            return False
    
    async def vectorize_image(self, image: ImageVector) -> bool:
        """向量化图片"""
        try:
            # 获取向量
            vector = await self.get_image_embedding(image.filename)
            
            # 存储到Qdrant
            point = PointStruct(
                id=str(image.id),
                vector=vector,
                payload={
                    "filename": image.filename,
                    "description": image.description,
                    "knowledge_base_id": str(image.knowledge_base_id),
                    "created_at": image.created_at.isoformat()
                }
            )
            
            self.qdrant_client.upsert(
                collection_name="image_vectors",
                points=[point]
            )
            
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
            filter_conditions = []
            if kb_ids:
                filter_conditions.append({
                    "key": "knowledge_base_id",
                    "match": {"any": kb_ids}
                })
            
            # 搜索
            search_result = self.qdrant_client.search(
                collection_name="text_vectors",
                query_vector=query_vector,
                query_filter={"must": filter_conditions} if filter_conditions else None,
                limit=top_k,
                with_payload=True
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "content": result.payload["content"],
                    "source_file": result.payload["source_file"],
                    "chunk_index": result.payload["chunk_index"],
                    "knowledge_base_id": result.payload["knowledge_base_id"]
                }
                for result in search_result
            ]
        except Exception as e:
            logger.error(f"Text search error: {e}")
            return []
    
    async def search_image(self, query: str, kb_ids: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """图片向量搜索"""
        try:
            # 获取查询向量（将文本查询转换为向量）
            query_vector = await self.get_text_embedding(query)
            
            # 构建过滤条件
            filter_conditions = []
            if kb_ids:
                filter_conditions.append({
                    "key": "knowledge_base_id",
                    "match": {"any": kb_ids}
                })
            
            # 搜索
            search_result = self.qdrant_client.search(
                collection_name="image_vectors",
                query_vector=query_vector,
                query_filter={"must": filter_conditions} if filter_conditions else None,
                limit=top_k,
                with_payload=True
            )
            
            return [
                {
                    "id": result.id,
                    "score": result.score,
                    "filename": result.payload["filename"],
                    "description": result.payload["description"],
                    "knowledge_base_id": result.payload["knowledge_base_id"]
                }
                for result in search_result
            ]
        except Exception as e:
            logger.error(f"Image search error: {e}")
            return []
    
    async def hybrid_search(self, query: str, kb_ids: List[str], top_k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """混合搜索（文本+图片）"""
        text_results = await self.search_text(query, kb_ids, top_k)
        image_results = await self.search_image(query, kb_ids, top_k)
        
        return {
            "text": text_results,
            "image": image_results
        } 