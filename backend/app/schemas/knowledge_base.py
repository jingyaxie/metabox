"""
知识库相关 Pydantic 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    type: Optional[str] = "text"
    is_public: Optional[str] = "private"
    # 新增模型选择字段
    text_model_id: Optional[str] = Field(None, description="文本理解模型ID")
    image_model_id: Optional[str] = Field(None, description="图片理解模型ID")
    embedding_model_id: Optional[str] = Field(None, description="文本嵌入模型ID")
    image_embedding_model_id: Optional[str] = Field(None, description="图片嵌入模型ID")

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = None
    is_public: Optional[str] = None
    # 新增模型选择字段
    text_model_id: Optional[str] = Field(None, description="文本理解模型ID")
    image_model_id: Optional[str] = Field(None, description="图片理解模型ID")
    embedding_model_id: Optional[str] = Field(None, description="文本嵌入模型ID")
    image_embedding_model_id: Optional[str] = Field(None, description="图片嵌入模型ID")

class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: str
    is_public: str
    owner_id: str
    created_at: str
    updated_at: str
    # 新增模型信息字段
    text_model_id: Optional[str] = None
    image_model_id: Optional[str] = None
    embedding_model_id: Optional[str] = None
    image_embedding_model_id: Optional[str] = None
    # 模型详细信息
    text_model_info: Optional[Dict[str, Any]] = None
    image_model_info: Optional[Dict[str, Any]] = None
    embedding_model_info: Optional[Dict[str, Any]] = None
    image_embedding_model_info: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class SmartConfigRequest(BaseModel):
    text: str = Field(..., description="待分析的文档内容")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="用户自定义参数")

class SmartConfigResponse(BaseModel):
    chunk_size: int = Field(..., description="推荐的分块大小")
    chunk_overlap: int = Field(..., description="推荐的重叠大小")
    embedding_model: str = Field(..., description="推荐的嵌入模型")
    reasoning: str = Field(..., description="推荐理由")
    confidence: float = Field(..., description="推荐置信度") 