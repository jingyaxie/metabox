"""
聊天服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

from app.models.chat import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse

class ChatService:
    """聊天服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """获取用户的聊天会话列表"""
        return self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc()).all()
    
    def get_session_by_id(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """根据ID获取聊天会话（检查权限）"""
        return self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
    
    def create_session(
        self, 
        user_id: str, 
        title: Optional[str], 
        kb_ids: Optional[List[str]]
    ) -> ChatSession:
        """创建聊天会话"""
        session = ChatSession(
            user_id=user_id,
            title=title or f"新对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            knowledge_base_ids=kb_ids or []
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    def delete_session(self, session_id: str, user_id: str) -> bool:
        """删除聊天会话"""
        session = self.get_session_by_id(session_id, user_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True
    
    async def process_chat(
        self,
        user_id: str,
        message: str,
        kb_ids: Optional[List[str]],
        history: Optional[List[Dict[str, Any]]],
        session_id: Optional[str]
    ) -> ChatResponse:
        """处理聊天请求"""
        # 获取或创建会话
        if session_id:
            session = self.get_session_by_id(session_id, user_id)
            if not session:
                raise ValueError("会话不存在或无权限访问")
        else:
            session = self.create_session(user_id, None, kb_ids)
        
        # 保存用户消息
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=message,
            message_type="text"
        )
        self.db.add(user_message)
        
        # TODO: 实现 RAG 检索和 LLM 生成
        # 这里应该调用 RAG 服务和 LLM 服务
        answer = f"这是对 '{message}' 的回复。RAG 功能正在开发中..."
        
        # 保存助手回复
        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            message_type="text"
        )
        self.db.add(assistant_message)
        
        # 更新会话时间
        session.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        return ChatResponse(
            answer=answer,
            session_id=str(session.id),
            message_id=str(assistant_message.id)
        ) 