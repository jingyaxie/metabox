"""
API 路由包
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .knowledge_base import router as kb_router
from .chat import router as chat_router
from .health import router as health_router

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(auth_router, prefix="/auth", tags=["认证"])
router.include_router(users_router, prefix="/users", tags=["用户"])
router.include_router(kb_router, prefix="/kb", tags=["知识库"])
router.include_router(chat_router, prefix="/chat", tags=["聊天"])
router.include_router(health_router, prefix="/health", tags=["健康检查"]) 