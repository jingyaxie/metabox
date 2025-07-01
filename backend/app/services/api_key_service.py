from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import time

from app.models.api_key import ApiKey, ApiKeyUsage, ApiKeyQuota
from app.schemas.api_key import (
    ApiKeyCreate, 
    ApiKeyUpdate, 
    ApiKeyResponse,
    ApiKeyUsageResponse,
    ApiKeyQuotaResponse
)
from app.core.exceptions import (
    ApiKeyNotFoundError,
    ApiKeyExpiredError,
    ApiKeyInactiveError,
    QuotaExceededError,
    RateLimitExceededError
)


class ApiKeyService:
    """API密钥管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_api_key(self, api_key_data: ApiKeyCreate, user_id: str = None) -> tuple[str, ApiKeyResponse]:
        """创建API密钥"""
        # 生成密钥
        key, key_hash, key_prefix = ApiKey.generate_key(
            app_id=api_key_data.app_id,
            app_name=api_key_data.app_name
        )
        
        # 创建API密钥记录
        api_key = ApiKey(
            app_id=api_key_data.app_id,
            app_name=api_key_data.app_name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=api_key_data.permissions,
            expires_at=api_key_data.expires_at,
            user_id=user_id
        )
        
        self.db.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)
        
        # 初始化配额记录
        self._init_quotas(api_key.id, api_key_data.permissions)
        
        return key, ApiKeyResponse.from_orm(api_key)

    def get_api_key_by_hash(self, key_hash: str) -> Optional[ApiKey]:
        """通过哈希值获取API密钥"""
        return self.db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()

    def get_api_key_by_prefix(self, key_prefix: str) -> Optional[ApiKey]:
        """通过前缀获取API密钥"""
        return self.db.query(ApiKey).filter(ApiKey.key_prefix == key_prefix).first()

    def get_api_key_by_id(self, api_key_id: str) -> Optional[ApiKey]:
        """通过ID获取API密钥"""
        return self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()

    def get_api_keys_by_user(self, user_id: str) -> List[ApiKeyResponse]:
        """获取用户的所有API密钥"""
        api_keys = self.db.query(ApiKey).filter(ApiKey.user_id == user_id).all()
        return [ApiKeyResponse.from_orm(api_key) for api_key in api_keys]

    def update_api_key(self, api_key_id: str, api_key_data: ApiKeyUpdate) -> ApiKeyResponse:
        """更新API密钥"""
        api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
        if not api_key:
            raise ApiKeyNotFoundError(f"API密钥 {api_key_id} 不存在")
        
        # 更新字段
        for field, value in api_key_data.dict(exclude_unset=True).items():
            setattr(api_key, field, value)
        
        self.db.commit()
        self.db.refresh(api_key)
        
        return ApiKeyResponse.from_orm(api_key)

    def delete_api_key(self, api_key_id: str) -> bool:
        """删除API密钥"""
        api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
        if not api_key:
            raise ApiKeyNotFoundError(f"API密钥 {api_key_id} 不存在")
        
        self.db.delete(api_key)
        self.db.commit()
        
        return True

    def validate_api_key(self, key: str, operation: str, kb_id: str = None) -> ApiKey:
        """验证API密钥"""
        # 获取密钥前缀
        if not key.startswith("metabox_"):
            raise ApiKeyNotFoundError("无效的API密钥格式")
        
        key_prefix = key[:20]
        api_key = self.get_api_key_by_prefix(key_prefix)
        
        if not api_key:
            raise ApiKeyNotFoundError("API密钥不存在")
        
        # 验证密钥有效性
        if not api_key.is_valid():
            if api_key.status == "expired":
                raise ApiKeyExpiredError("API密钥已过期")
            else:
                raise ApiKeyInactiveError("API密钥已停用")
        
        # 验证权限
        if not api_key.has_permission(operation, kb_id):
            raise ApiKeyInactiveError(f"没有 {operation} 操作的权限")
        
        # 检查频率限制
        if not self._check_rate_limit(api_key):
            raise RateLimitExceededError("请求频率超限")
        
        # 检查配额
        if not self._check_quota(api_key):
            raise QuotaExceededError("配额已用完")
        
        return api_key

    def record_api_usage(self, api_key_id: str, endpoint: str, method: str, 
                        status_code: int, tokens_used: int = 0, response_time: int = 0):
        """记录API使用情况"""
        # 记录使用情况
        usage = ApiKeyUsage(
            api_key_id=api_key_id,
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            tokens_used=tokens_used,
            response_time=response_time
        )
        
        self.db.add(usage)
        
        # 更新API密钥统计
        api_key = self.db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
        if api_key:
            api_key.update_usage(tokens_used)
        
        # 更新配额使用量
        self._update_quota_usage(api_key_id)
        
        self.db.commit()

    def get_api_key_usage(self, api_key_id: str, days: int = 30) -> List[ApiKeyUsageResponse]:
        """获取API密钥使用记录"""
        start_date = datetime.now() - timedelta(days=days)
        
        usage_records = self.db.query(ApiKeyUsage).filter(
            and_(
                ApiKeyUsage.api_key_id == api_key_id,
                ApiKeyUsage.created_at >= start_date
            )
        ).order_by(ApiKeyUsage.created_at.desc()).all()
        
        return [ApiKeyUsageResponse.from_orm(record) for record in usage_records]

    def get_api_key_quota(self, api_key_id: str) -> List[ApiKeyQuotaResponse]:
        """获取API密钥配额信息"""
        quotas = self.db.query(ApiKeyQuota).filter(
            ApiKeyQuota.api_key_id == api_key_id
        ).all()
        
        return [ApiKeyQuotaResponse.from_orm(quota) for quota in quotas]

    def _init_quotas(self, api_key_id: str, permissions: Dict[str, Any]):
        """初始化配额记录"""
        now = datetime.now()
        
        # 日配额
        daily_quota = ApiKeyQuota(
            api_key_id=api_key_id,
            quota_type="daily",
            quota_limit=permissions.get("quota_daily", 10000),
            quota_used=0,
            quota_reset_at=now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        )
        
        # 月配额
        monthly_quota = ApiKeyQuota(
            api_key_id=api_key_id,
            quota_type="monthly",
            quota_limit=permissions.get("quota_monthly", 300000),
            quota_used=0,
            quota_reset_at=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)
        )
        
        self.db.add(daily_quota)
        self.db.add(monthly_quota)
        self.db.commit()

    def _check_rate_limit(self, api_key: ApiKey) -> bool:
        """检查频率限制"""
        rate_limit = api_key.permissions.get("rate_limit", 1000)
        
        # 检查最近一分钟的调用次数
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_calls = self.db.query(ApiKeyUsage).filter(
            and_(
                ApiKeyUsage.api_key_id == api_key.id,
                ApiKeyUsage.created_at >= one_minute_ago
            )
        ).count()
        
        return recent_calls < rate_limit

    def _check_quota(self, api_key: ApiKey) -> bool:
        """检查配额限制"""
        quotas = self.db.query(ApiKeyQuota).filter(
            ApiKeyQuota.api_key_id == api_key.id
        ).all()
        
        for quota in quotas:
            # 检查是否需要重置配额
            if quota.quota_reset_at <= datetime.now():
                quota.quota_used = 0
                if quota.quota_type == "daily":
                    quota.quota_reset_at = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
                else:  # monthly
                    quota.quota_reset_at = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32)
            
            # 检查配额是否超限
            if quota.quota_used >= quota.quota_limit:
                return False
        
        return True

    def _update_quota_usage(self, api_key_id: str):
        """更新配额使用量"""
        quotas = self.db.query(ApiKeyQuota).filter(
            ApiKeyQuota.api_key_id == api_key_id
        ).all()
        
        for quota in quotas:
            quota.quota_used += 1 