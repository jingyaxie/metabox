"""
轻量级配置模块
使用轻量级替代方案，降低硬件要求
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings


class LightweightConfig(BaseSettings):
    """轻量级配置类"""
    
    # 数据库配置 - 使用SQLite替代PostgreSQL
    DATABASE_URL: str = "sqlite:///./metabox.db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # 向量数据库配置 - 使用Chroma替代Qdrant
    VECTOR_DB_TYPE: str = "chroma"
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    VECTOR_DIMENSION: int = 1536
    
    # 存储配置 - 使用本地文件存储
    STORAGE_TYPE: str = "local"
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB，支持图片
    
    # 模型配置 - 使用API调用
    MODEL_TYPE: str = "api"
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    API_TIMEOUT: int = 30
    
    # 缓存配置 - 使用内存缓存替代Redis
    CACHE_TYPE: str = "memory"
    CACHE_TTL: int = 3600  # 1小时
    MAX_CACHE_SIZE: int = 500  # 最大缓存条目数
    
    # 资源限制 - 降低资源消耗
    MAX_CONCURRENT_REQUESTS: int = 5
    MAX_DOCUMENT_SIZE: int = 5 * 1024 * 1024  # 5MB，支持图片
    MAX_CHUNK_SIZE: int = 500
    MAX_CHUNKS_PER_DOC: int = 50  # 增加分块数量支持图片
    
    # 内存优化
    ENABLE_MEMORY_OPTIMIZATION: bool = True
    MAX_MEMORY_USAGE: int = 512  # MB，增加内存支持图片处理
    CLEANUP_INTERVAL: int = 300  # 5分钟
    
    # 功能开关 - 保留图片向量化功能
    ENABLE_RERANK: bool = False  # 关闭重排序
    ENABLE_HYBRID_SEARCH: bool = False  # 关闭混合搜索
    ENABLE_STREAMING: bool = True  # 保留流式响应
    ENABLE_MULTIMODAL: bool = True  # 启用多模态，支持图片向量化
    ENABLE_ADVANCED_SEARCH: bool = False  # 关闭高级搜索
    
    # 图片处理配置
    ENABLE_IMAGE_VECTORIZATION: bool = True  # 启用图片向量化
    IMAGE_VECTOR_MODEL: str = "clip"  # 使用CLIP模型
    IMAGE_MAX_SIZE: int = 1024  # 图片最大尺寸
    IMAGE_QUALITY: int = 85  # 图片质量
    
    # 检索配置 - 简化检索
    MAX_SEARCH_RESULTS: int = 10  # 增加结果数量
    SEARCH_TIMEOUT: int = 15  # 增加超时时间
    
    # 监控配置
    ENABLE_METRICS: bool = False
    ENABLE_HEALTH_CHECK: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_database_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return {
            "url": self.DATABASE_URL,
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "use_sqlite": True
        }
    
    def get_vector_db_config(self) -> Dict[str, Any]:
        """获取向量数据库配置"""
        return {
            "type": self.VECTOR_DB_TYPE,
            "chroma_persist_dir": self.CHROMA_PERSIST_DIR,
            "dimension": self.VECTOR_DIMENSION,
            "use_chroma": True
        }
    
    def get_storage_config(self) -> Dict[str, Any]:
        """获取存储配置"""
        return {
            "type": self.STORAGE_TYPE,
            "upload_dir": self.UPLOAD_DIR,
            "max_file_size": self.MAX_FILE_SIZE,
            "use_local_storage": True
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        return {
            "type": self.MODEL_TYPE,
            "default_model": self.DEFAULT_MODEL,
            "timeout": self.API_TIMEOUT
        }
    
    def get_cache_config(self) -> Dict[str, Any]:
        """获取缓存配置"""
        return {
            "type": self.CACHE_TYPE,
            "ttl": self.CACHE_TTL,
            "max_size": self.MAX_CACHE_SIZE,
            "use_memory_cache": True
        }
    
    def get_optimization_config(self) -> Dict[str, Any]:
        """获取优化配置"""
        return {
            "max_concurrent": self.MAX_CONCURRENT_REQUESTS,
            "max_doc_size": self.MAX_DOCUMENT_SIZE,
            "max_chunk_size": self.MAX_CHUNK_SIZE,
            "max_chunks_per_doc": self.MAX_CHUNKS_PER_DOC,
            "memory_optimization": self.ENABLE_MEMORY_OPTIMIZATION,
            "max_memory": self.MAX_MEMORY_USAGE,
            "cleanup_interval": self.CLEANUP_INTERVAL,
        }
    
    def get_image_config(self) -> Dict[str, Any]:
        """获取图片处理配置"""
        return {
            "enable_image_vectorization": self.ENABLE_IMAGE_VECTORIZATION,
            "image_vector_model": self.IMAGE_VECTOR_MODEL,
            "image_max_size": self.IMAGE_MAX_SIZE,
            "image_quality": self.IMAGE_QUALITY,
            "enable_multimodal": self.ENABLE_MULTIMODAL
        }
    
    def get_feature_flags(self) -> Dict[str, bool]:
        """获取功能开关"""
        return {
            "enable_rerank": self.ENABLE_RERANK,
            "enable_hybrid_search": self.ENABLE_HYBRID_SEARCH,
            "enable_streaming": self.ENABLE_STREAMING,
            "enable_multimodal": self.ENABLE_MULTIMODAL,
            "enable_advanced_search": self.ENABLE_ADVANCED_SEARCH,
            "enable_image_vectorization": self.ENABLE_IMAGE_VECTORIZATION,
            "lightweight_mode": True
        }


# 全局配置实例
lightweight_config = LightweightConfig() 