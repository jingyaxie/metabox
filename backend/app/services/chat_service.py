"""
聊天服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, AsyncGenerator
import uuid
from datetime import datetime
import asyncio

from app.models.chat import ChatSession, ChatMessage
from app.models.knowledge_base import KnowledgeBase, TextChunk
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
        
        # 执行 RAG 检索
        answer = await self._rag_search(message, kb_ids or [])
        
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
    
    async def process_chat_stream(
        self,
        session_id: str,
        message: str,
        kb_ids: List[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """处理流式聊天请求"""
        # 保存用户消息
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=message,
            message_type="text"
        )
        self.db.add(user_message)
        self.db.commit()
        
        # 执行 RAG 检索并流式返回
        answer = await self._rag_search(message, kb_ids)
        
        # 流式返回答案
        words = answer.split()
        for i, word in enumerate(words):
            yield {
                "type": "chunk",
                "content": word + " ",
                "is_end": i == len(words) - 1
            }
            await asyncio.sleep(0.1)  # 模拟流式效果
        
        # 保存助手回复
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=answer,
            message_type="text"
        )
        self.db.add(assistant_message)
        
        # 更新会话时间
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session:
            session.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        yield {
            "type": "complete",
            "message_id": str(assistant_message.id)
        }
    
    async def _rag_search(self, query: str, kb_ids: List[str]) -> str:
        """RAG 检索"""
        if not kb_ids:
            return f"这是对 '{query}' 的回复。请先选择知识库以获取更准确的答案。"
        
        # 获取知识库内容
        chunks = []
        for kb_id in kb_ids:
            kb_chunks = self.db.query(TextChunk).filter(
                TextChunk.knowledge_base_id == kb_id
            ).all()
            chunks.extend(kb_chunks)
        
        if not chunks:
            return f"这是对 '{query}' 的回复。所选知识库暂无内容，请先上传文档。"
        
        # 简单的关键词匹配（实际项目中应使用向量检索）
        relevant_chunks = []
        query_words = query.lower().split()
        
        for chunk in chunks:
            content_lower = chunk.content.lower()
            score = sum(1 for word in query_words if word in content_lower)
            if score > 0:
                relevant_chunks.append((chunk, score))
        
        # 按相关性排序
        relevant_chunks.sort(key=lambda x: x[1], reverse=True)
        
        if relevant_chunks:
            # 构建基于检索结果的回答
            top_chunks = relevant_chunks[:3]  # 取前3个最相关的分块
            context = "\n".join([chunk.content for chunk, _ in top_chunks])
            
            answer = f"""基于知识库内容，为您提供以下回答：

问题：{query}

相关参考：
{context}

回答：根据检索到的相关内容，{query} 的相关信息如上所示。如需更详细的解答，请提供更具体的问题。"""
        else:
            answer = f"抱歉，在知识库中未找到与 '{query}' 直接相关的内容。请尝试使用其他关键词或检查知识库是否包含相关信息。"
        
        return answer 