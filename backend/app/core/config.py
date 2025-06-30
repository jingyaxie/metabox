"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "MetaBox"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "postgresql://kb_user:kb_password@postgres:5432/metabox"
    QDRANT_URL: str = "http://qdrant:6333"
    
    # AI 模型配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    QWEN_API_KEY: Optional[str] = None
    QWEN_BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"
    
    # 认证配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文件上传配置
    MAX_FILE_SIZE: int = 104857600  # 100MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "doc", "docx", "txt", "md", "jpg", "jpeg", "png", "gif"]
    
    # 缓存配置
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # 1小时
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/metabox.log"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # 向量模型配置
    TEXT_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    TEXT_EMBEDDING_DIMENSION: int = 1536
    IMAGE_EMBEDDING_MODEL: str = "clip-vit-base-patch32"
    IMAGE_EMBEDDING_DIMENSION: int = 512
    
    # RAG 配置
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # 插件配置
    PLUGINS_ENABLED: bool = True
    PLUGINS_DIR: str = "plugins"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建全局配置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True) 