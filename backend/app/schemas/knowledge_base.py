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

class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = None
    is_public: Optional[str] = None

class KnowledgeBaseResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    type: str
    owner_id: UUID
    is_public: str
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True

class SmartConfigRequest(BaseModel):
    text: str = Field(..., description="待分析的文档内容")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="用户自定义参数")

class SmartConfigResponse(BaseModel):
    detected_type: str = Field(..., description="检测到的文档类型")
    confidence: float = Field(..., description="类型置信度")
    config: Dict[str, Any] = Field(..., description="推荐参数配置")
    errors: Optional[List[str]] = Field(None, description="配置验证错误")
    valid: Optional[bool] = Field(True, description="配置是否有效") 