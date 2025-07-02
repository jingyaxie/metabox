# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
MetaBox 后端应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.core.config import settings
from app.api import router
from app.plugins.init_plugins import init_plugins

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="MetaBox API",
    description="本地智能知识库系统 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 包含路由
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("MetaBox API 启动中...")
    
    # 初始化插件系统
    if init_plugins():
        logger.info("插件系统初始化成功")
    else:
        logger.error("插件系统初始化失败")

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "MetaBox API",
        "version": "1.0.0"
    }

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Welcome to MetaBox API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    ) 