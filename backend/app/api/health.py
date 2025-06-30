"""
健康检查 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@router.get("/db")
async def database_health_check(db: Session = Depends(get_db)):
    """数据库健康检查"""
    try:
        # 执行简单查询测试数据库连接
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """详细健康检查"""
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # 数据库检查
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # 配置检查
    try:
        health_status["checks"]["config"] = "healthy"
        health_status["config"] = {
            "debug": settings.DEBUG,
            "upload_dir": settings.UPLOAD_DIR,
            "max_file_size": settings.MAX_FILE_SIZE
        }
    except Exception as e:
        health_status["checks"]["config"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status 