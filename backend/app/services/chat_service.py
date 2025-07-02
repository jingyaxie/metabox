"""
聊天服务
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime
import asyncio
import logging

from app.models.chat import ChatSession, ChatMessage
from app.models.knowledge_base import TextChunk, ImageVector
from app.schemas.chat import ChatResponse
from app.services.vector_service import VectorService
from app.core.config import settings

logger = logging.getLogger(__name__)

class ChatService:
    """聊天服务类"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_service = VectorService(db)
    
    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """获取用户的聊天会话列表"""
        return self.db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc()).all()
    
    def get_session_by_id(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """根据ID获取会话（检查权限）"""
        return self.db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
    
    def get_session_messages(self, session_id: str, user_id: str) -> List[ChatMessage]:
        """获取会话消息"""
        # 先检查权限
        session = self.get_session_by_id(session_id, user_id)
        if not session:
            return []
        
        return self.db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at).all()
    
    def create_session(self, user_id: str, name: Optional[str], kb_ids: Optional[List[str]]) -> ChatSession:
        """创建新的聊天会话"""
        session = ChatSession(
            user_id=user_id,
            name=name or f"新对话 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            knowledge_base_ids=kb_ids or []
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
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
        """RAG 检索 - 使用向量化引擎"""
        if not kb_ids:
            return f"这是对 '{query}' 的回复。请先选择知识库以获取更准确的答案。"
        
        try:
            # 使用向量化服务进行混合搜索
            search_results = await self.vector_service.hybrid_search(
                query, 
                kb_ids, 
                top_k=settings.TOP_K_RESULTS
            )
            
            text_results = search_results["text"]
            image_results = search_results["image"]
            
            if not text_results and not image_results:
                return f"抱歉，在知识库中未找到与 '{query}' 直接相关的内容。请尝试使用其他关键词或检查知识库是否包含相关信息。"
            
            # 构建上下文
            context_parts = []
            
            # 添加文本结果
            if text_results:
                context_parts.append("相关文本内容：")
                for i, result in enumerate(text_results[:3], 1):
                    context_parts.append(f"{i}. {result['content'][:200]}...")
            
            # 添加图片结果
            if image_results:
                context_parts.append("\n相关图片：")
                for i, result in enumerate(image_results[:2], 1):
                    image_url = result["metadata"].get("image_url", "")
                    context_parts.append(f"{i}. {result['description']}")
                    if image_url:
                        context_parts.append(f"   图片链接：{image_url}")
            
            context = "\n".join(context_parts)
            
            # 构建回答
            answer = f"""基于知识库内容，为您提供以下回答：

问题：{query}

{context}

回答：根据检索到的相关内容，{query} 的相关信息如上所示。"""
            
            # 如果有高相关性结果，提供更具体的回答
            if text_results and text_results[0]["score"] > 0.8:
                best_match = text_results[0]["content"]
                answer += f"\n\n最相关的信息：{best_match[:300]}..."
            
            return answer
            
        except Exception as e:
            logger.error(f"RAG search error: {e}")
            # 降级到关键词匹配
            return self._fallback_keyword_search(query, kb_ids)
    
    def _fallback_keyword_search(self, query: str, kb_ids: List[str]) -> str:
        """降级关键词搜索"""
        # 获取知识库内容
        chunks = []
        for kb_id in kb_ids:
            kb_chunks = self.db.query(TextChunk).filter(
                TextChunk.knowledge_base_id == kb_id
            ).all()
            chunks.extend(kb_chunks)
        
        if not chunks:
            return f"这是对 '{query}' 的回复。所选知识库暂无内容，请先上传文档。"
        
        # 简单的关键词匹配
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