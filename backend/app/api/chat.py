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
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
security = HTTPBearer()

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

@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    db: Session = Depends(get_db)
):
    """WebSocket 聊天接口"""
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 处理消息
            chat_service = ChatService(db)
            response = await chat_service.process_chat_stream(
                session_id=session_id,
                message=message_data.get("message", ""),
                kb_ids=message_data.get("kb_ids", [])
            )
            
            # 发送流式响应
            for chunk in response:
                await websocket.send_text(json.dumps(chunk))
                
    except WebSocketDisconnect:
        print("WebSocket 连接断开")
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        })) 