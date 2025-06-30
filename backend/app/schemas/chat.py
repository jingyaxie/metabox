"""
聊天相关的数据模式
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    kb_ids: Optional[List[str]] = None
    history: Optional[List[Dict[str, Any]]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    """聊天响应"""
    answer: str
    session_id: str
    message_id: str
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

class ChatSessionCreate(BaseModel):
    """创建聊天会话"""
    title: Optional[str] = None
    kb_ids: Optional[List[str]] = None

class ChatSessionResponse(BaseModel):
    """聊天会话响应"""
    id: str
    title: Optional[str]
    user_id: str
    knowledge_base_ids: Optional[List[str]]
    model_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int

    class Config:
        from_attributes = True 