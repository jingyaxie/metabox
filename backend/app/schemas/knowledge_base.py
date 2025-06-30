"""
知识库相关 Pydantic 数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional
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