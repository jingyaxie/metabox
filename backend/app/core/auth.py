from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import time

from app.core.database import get_db
from app.services.api_key_service import ApiKeyService
from app.core.exceptions import (
    ApiKeyNotFoundError,
    ApiKeyExpiredError,
    ApiKeyInactiveError,
    QuotaExceededError,
    RateLimitExceededError
)

# HTTP Bearer认证
security = HTTPBearer(auto_error=False)


async def get_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[str]:
    """获取API密钥"""
    # 优先从Authorization header获取
    if credentials:
        return credentials.credentials
    
    # 从X-API-Key header获取
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return api_key
    
    return None


async def validate_api_key(
    operation: str,
    kb_id: str = None,
    api_key: Optional[str] = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """验证API密钥"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "MISSING_API_KEY",
                    "message": "缺少API密钥"
                }
            }
        )
    
    try:
        api_key_service = ApiKeyService(db)
        validated_key = api_key_service.validate_api_key(api_key, operation, kb_id)
        return validated_key
    except ApiKeyNotFoundError:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "无效的API密钥"
                }
            }
        )
    except ApiKeyExpiredError:
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error": {
                    "code": "API_KEY_EXPIRED",
                    "message": "API密钥已过期"
                }
            }
        )
    except ApiKeyInactiveError as e:
        raise HTTPException(
            status_code=403,
            detail={
                "success": False,
                "error": {
                    "code": "API_KEY_INACTIVE",
                    "message": str(e)
                }
            }
        )
    except RateLimitExceededError:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "请求频率超限，请稍后重试",
                    "retry_after": 60
                }
            },
            headers={
                "X-RateLimit-Limit": "1000",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + 60),
                "Retry-After": "60"
            }
        )
    except QuotaExceededError:
        raise HTTPException(
            status_code=429,
            detail={
                "success": False,
                "error": {
                    "code": "QUOTA_EXCEEDED",
                    "message": "配额已用完"
                }
            }
        )


async def record_api_usage(
    request: Request,
    api_key,
    status_code: int,
    tokens_used: int = 0,
    db: Session = Depends(get_db)
):
    """记录API使用情况"""
    start_time = getattr(request.state, 'start_time', time.time())
    response_time = int((time.time() - start_time) * 1000)  # 转换为毫秒
    
    api_key_service = ApiKeyService(db)
    api_key_service.record_api_usage(
        api_key_id=api_key.id,
        endpoint=request.url.path,
        method=request.method,
        status_code=status_code,
        tokens_used=tokens_used,
        response_time=response_time
    )


# 依赖函数
def require_api_key(operation: str):
    """要求API密钥的依赖函数"""
    async def _require_api_key(
        api_key = Depends(lambda: validate_api_key(operation))
    ):
        return api_key
    return _require_api_key


def require_query_permission():
    """要求查询权限的依赖函数"""
    return require_api_key("query")


def require_search_permission():
    """要求检索权限的依赖函数"""
    return require_api_key("search")


def require_read_permission():
    """要求读取权限的依赖函数"""
    return require_api_key("read") 