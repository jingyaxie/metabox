"""
聊天 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.chat_service import ChatService
from app.services.admin_service import AdminService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
security = HTTPBearer()

@router.get("/models")
async def get_available_models(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取可用的聊天模型列表"""
    try:
        auth_service = AuthService(db)
        admin_service = AdminService(db)
        
        # 验证当前用户
        current_user = auth_service.get_current_user(credentials.credentials)
        
        # 获取所有活跃的模型配置
        model_configs = admin_service.get_model_configs(
            model_type="chat",  # 聊天模型类型
            active_only=True
        )
        
        # 转换为前端需要的格式
        models = []
        for config in model_configs:
            # 获取供应商信息
            provider = admin_service.get_model_provider_by_id(config.provider_id)
            if provider and provider.is_active:
                models.append({
                    "id": config.model_name,
                    "name": config.display_name,
                    "provider": provider.display_name,
                    "description": f"{provider.display_name} - {config.display_name}",
                    "max_tokens": config.max_tokens or 4096,
                    "temperature": float(config.temperature) if config.temperature else 0.7,
                    "is_default": config.is_default,
                    "provider_type": provider.provider_type
                })
        
        # 如果没有配置的模型，返回默认模型
        if not models:
            models = [
                {
                    "id": "gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "OpenAI",
                    "description": "快速、高效的对话模型",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "is_default": True,
                    "provider_type": "openai"
                },
                {
                    "id": "gpt-4",
                    "name": "GPT-4",
                    "provider": "OpenAI",
                    "description": "更强大的推理能力",
                    "max_tokens": 8192,
                    "temperature": 0.7,
                    "is_default": False,
                    "provider_type": "openai"
                }
            ]
        
        return models
        
    except Exception as e:
        # 如果出错，返回默认模型
        return [
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "provider": "OpenAI",
                "description": "快速、高效的对话模型",
                "max_tokens": 4096,
                "temperature": 0.7,
                "is_default": True,
                "provider_type": "openai"
            }
        ]

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """聊天对话"""
    auth_service = AuthService(db)
    chat_service = ChatService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 处理聊天请求
    response = await chat_service.process_chat(
        user_id=current_user.id,
        message=request.message,
        kb_ids=request.kb_ids,
        history=request.history,
        session_id=request.session_id
    )
    
    return response

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket聊天接口"""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 处理消息
            chat_service = ChatService(db)
            response = await chat_service.process_chat(
                user_id=message_data.get("user_id"),
                message=message_data.get("message"),
                kb_ids=message_data.get("kb_ids"),
                history=message_data.get("history"),
                session_id=session_id
            )
            
            # 发送响应
            await websocket.send_text(json.dumps({
                "type": "message",
                "data": response.dict()
            }))
            
    except WebSocketDisconnect:
        print(f"WebSocket断开连接: {session_id}")

@router.post("/sessions")
async def create_chat_session(
    title: Optional[str] = None,
    kb_ids: Optional[List[str]] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """创建聊天会话"""
    auth_service = AuthService(db)
    chat_service = ChatService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 创建聊天会话
    session = chat_service.create_session(
        user_id=current_user.id,
        title=title,
        kb_ids=kb_ids
    )
    
    return session

@router.get("/sessions")
async def get_chat_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取聊天会话列表"""
    auth_service = AuthService(db)
    chat_service = ChatService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取用户的聊天会话
    sessions = chat_service.get_user_sessions(current_user.id)
    return sessions

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取会话消息"""
    auth_service = AuthService(db)
    chat_service = ChatService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取会话消息
    messages = chat_service.get_session_messages(session_id, current_user.id)
    return messages

@router.get("/sessions/{session_id}")
async def get_chat_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取聊天会话详情"""
    auth_service = AuthService(db)
    chat_service = ChatService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取聊天会话
    session = chat_service.get_session_by_id(session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天会话不存在或无权限访问"
        )
    
    return session

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """删除聊天会话"""
    auth_service = AuthService(db)
    chat_service = ChatService(db)
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 删除聊天会话
    success = chat_service.delete_session(session_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="聊天会话不存在或无权限删除"
        )
    
    return {"message": "聊天会话删除成功"} 