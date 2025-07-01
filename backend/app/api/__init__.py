"""
API 路由包
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .knowledge_base import router as kb_router
from .chat import router as chat_router
from .plugins import router as plugins_router
from .health import router as health_router
from .smart_config import router as smart_config_router
from .enhanced_retrieval import router as enhanced_retrieval_router
from .v1.api_keys import router as api_keys_router
from .v1.external import router as external_router

# 创建主路由
router = APIRouter()

# 注册子路由
router.include_router(auth_router, prefix="/auth", tags=["认证"])
router.include_router(users_router, prefix="/users", tags=["用户"])
router.include_router(kb_router, prefix="/kb", tags=["知识库"])
router.include_router(chat_router, prefix="/chat", tags=["聊天"])
router.include_router(plugins_router, prefix="/plugins", tags=["插件管理"])
router.include_router(health_router, prefix="/health", tags=["健康检查"])
router.include_router(smart_config_router, prefix="/kb", tags=["智能配置"])
router.include_router(enhanced_retrieval_router, tags=["增强检索"])
router.include_router(api_keys_router, tags=["API密钥管理"])
router.include_router(external_router, tags=["外部API"]) 