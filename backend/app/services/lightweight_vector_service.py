"""
轻量级向量数据库服务
使用 Chroma 替代 Qdrant，降低资源消耗
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import numpy as np

from app.core.lightweight_config import lightweight_config
from app.utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class LightweightVectorService:
    """轻量级向量数据库服务"""
    
    def __init__(self):
        self.config = lightweight_config.get_vector_db_config()
        self.text_processor = TextProcessor()
        
        # 初始化 Chroma 客户端
        self._init_chroma_client()
        
        # 内存缓存
        self.collection_cache = {}
        self.vector_cache = {}
        self.max_cache_size = 500  # 降低缓存大小
    
    def _init_chroma_client(self):
        """初始化 Chroma 客户端"""
        try:
            import chromadb
            from chromadb.config import Settings
            
            # 确保持久化目录存在
            persist_dir = self.config["chroma_persist_dir"]
            os.makedirs(persist_dir, exist_ok=True)
            
            # 创建客户端
            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,  # 关闭遥测
                    allow_reset=True
                )
            )
            
            logger.info(f"Chroma 客户端初始化成功，持久化目录: {persist_dir}")
            
        except ImportError:
            logger.error("Chroma 未安装，请运行: pip install chromadb")
            self.chroma_client = None
        except Exception as e:
            logger.error(f"Chroma 客户端初始化失败: {e}")
            self.chroma_client = None
    
    async def create_collection(self, collection_name: str, dimension: int = 1536) -> bool:
        """创建集合"""
        try:
            if not self.chroma_client:
                return False
            
            # 检查集合是否已存在
            try:
                collection = self.chroma_client.get_collection(collection_name)
                logger.info(f"集合 {collection_name} 已存在")
                return True
            except:
                pass
            
            # 创建新集合
            collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={
                    "dimension": dimension,
                    "created_at": datetime.now().isoformat(),
                    "description": f"Collection for {collection_name}"
                }
            )
            
            # 缓存集合
            self.collection_cache[collection_name] = collection
            
            logger.info(f"集合 {collection_name} 创建成功")
            return True
            
        except Exception as e:
            logger.error(f"创建集合失败: {e}")
            return False
    
    async def upsert_vectors(
        self, 
        collection_name: str, 
        vectors: List[Dict[str, Any]]
    ) -> bool:
        """插入或更新向量"""
        try:
            if not self.chroma_client:
                return False
            
            # 获取集合
            collection = await self._get_collection(collection_name)
            if not collection:
                return False
            
            # 准备数据
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for vector in vectors:
                ids.append(str(vector["id"]))
                embeddings.append(vector["vector"])
                documents.append(vector.get("content", ""))
                metadatas.append(vector.get("metadata", {}))
            
            # 批量插入
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            # 更新缓存
            self._update_vector_cache(collection_name, vectors)
            
            logger.info(f"成功插入 {len(vectors)} 个向量到集合 {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"插入向量失败: {e}")
            return False
    
    async def search_vectors(
        self, 
        collection_name: str, 
        query_vector: List[float], 
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """搜索向量"""
        try:
            if not self.chroma_client:
                return []
            
            # 获取集合
            collection = await self._get_collection(collection_name)
            if not collection:
                return []
            
            # 构建查询
            where_filter = None
            if filter_metadata:
                where_filter = self._build_chroma_filter(filter_metadata)
            
            # 执行搜索
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
                        "score": 1.0 - results["distances"][0][i],  # 转换为相似度分数
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "content": results["documents"][0][i] if results["documents"] else ""
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"搜索向量失败: {e}")
            return []
    
    def _build_chroma_filter(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """构建 Chroma 过滤器"""
        # Chroma 使用 $and, $or 等操作符
        filters = []
        
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                filters.append({key: {"$eq": value}})
            elif isinstance(value, list):
                filters.append({key: {"$in": value}})
        
        if len(filters) == 1:
            return filters[0]
        elif len(filters) > 1:
            return {"$and": filters}
        else:
            return {}
    
    async def delete_collection(self, collection_name: str) -> bool:
        """删除集合"""
        try:
            if not self.chroma_client:
                return False
            
            self.chroma_client.delete_collection(collection_name)
            
            # 清理缓存
            if collection_name in self.collection_cache:
                del self.collection_cache[collection_name]
            if collection_name in self.vector_cache:
                del self.vector_cache[collection_name]
            
            logger.info(f"集合 {collection_name} 删除成功")
            return True
            
        except Exception as e:
            logger.error(f"删除集合失败: {e}")
            return False
    
    async def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """获取集合信息"""
        try:
            if not self.chroma_client:
                return {}
            
            collection = await self._get_collection(collection_name)
            if not collection:
                return {}
            
            # 获取集合统计信息
            count = collection.count()
            
            return {
                "name": collection_name,
                "count": count,
                "metadata": collection.metadata,
                "created_at": collection.metadata.get("created_at", "")
            }
            
        except Exception as e:
            logger.error(f"获取集合信息失败: {e}")
            return {}
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """列出所有集合"""
        try:
            if not self.chroma_client:
                return []
            
            collections = self.chroma_client.list_collections()
            
            collection_info = []
            for collection in collections:
                info = await self.get_collection_info(collection.name)
                if info:
                    collection_info.append(info)
            
            return collection_info
            
        except Exception as e:
            logger.error(f"列出集合失败: {e}")
            return []
    
    async def _get_collection(self, collection_name: str):
        """获取集合（带缓存）"""
        try:
            # 检查缓存
            if collection_name in self.collection_cache:
                return self.collection_cache[collection_name]
            
            # 从客户端获取
            collection = self.chroma_client.get_collection(collection_name)
            
            # 缓存集合
            self.collection_cache[collection_name] = collection
            
            # 限制缓存大小
            if len(self.collection_cache) > self.max_cache_size:
                # 删除最旧的缓存
                oldest_key = next(iter(self.collection_cache))
                del self.collection_cache[oldest_key]
            
            return collection
            
        except Exception as e:
            logger.error(f"获取集合失败: {e}")
            return None
    
    def _update_vector_cache(self, collection_name: str, vectors: List[Dict[str, Any]]):
        """更新向量缓存"""
        try:
            if collection_name not in self.vector_cache:
                self.vector_cache[collection_name] = {}
            
            for vector in vectors:
                self.vector_cache[collection_name][str(vector["id"])] = vector
            
            # 限制缓存大小
            if len(self.vector_cache[collection_name]) > self.max_cache_size:
                # 删除最旧的缓存
                oldest_keys = list(self.vector_cache[collection_name].keys())[:50]
                for key in oldest_keys:
                    del self.vector_cache[collection_name][key]
                    
        except Exception as e:
            logger.error(f"更新向量缓存失败: {e}")
    
    async def clear_cache(self):
        """清理缓存"""
        try:
            self.collection_cache.clear()
            self.vector_cache.clear()
            logger.info("向量服务缓存已清理")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        try:
            collections = await self.list_collections()
            total_vectors = sum(col["count"] for col in collections)
            
            return {
                "service": "lightweight_vector",
                "status": "running" if self.chroma_client else "error",
                "collections_count": len(collections),
                "total_vectors": total_vectors,
                "cache_size": len(self.collection_cache),
                "vector_cache_size": sum(len(cache) for cache in self.vector_cache.values())
            }
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            return {"status": "error", "error": str(e)}


# 全局实例
lightweight_vector_service = LightweightVectorService() 