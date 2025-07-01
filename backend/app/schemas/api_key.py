from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ApiKeyPermissions(BaseModel):
    """API密钥权限配置"""
    operations: List[str] = Field(
        default=["query", "search", "read"],
        description="允许的操作类型"
    )
    kb_ids: List[str] = Field(
        default=[],
        description="可访问的知识库ID列表，空列表表示可访问所有"
    )
    rate_limit: int = Field(
        default=1000,
        description="每分钟调用限制"
    )
    quota_daily: int = Field(
        default=10000,
        description="每日配额"
    )
    quota_monthly: int = Field(
        default=300000,
        description="每月配额"
    )
    max_tokens: int = Field(
        default=4000,
        description="单次请求最大Token数"
    )


class ApiKeyCreate(BaseModel):
    """创建API密钥请求"""
    app_id: str = Field(..., description="应用ID")
    app_name: str = Field(..., description="应用名称")
    permissions: ApiKeyPermissions = Field(
        default_factory=ApiKeyPermissions,
        description="权限配置"
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="过期时间"
    )


class ApiKeyUpdate(BaseModel):
    """更新API密钥请求"""
    app_name: Optional[str] = Field(None, description="应用名称")
    permissions: Optional[ApiKeyPermissions] = Field(None, description="权限配置")
    status: Optional[str] = Field(None, description="状态")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class ApiKeyResponse(BaseModel):
    """API密钥响应"""
    id: str
    app_id: str
    app_name: str
    key_prefix: str
    permissions: Dict[str, Any]
    status: str
    created_at: datetime
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    total_calls: int
    total_tokens: int
    user_id: Optional[str]

    class Config:
        from_attributes = True


class ApiKeyUsageResponse(BaseModel):
    """API密钥使用记录响应"""
    id: str
    api_key_id: str
    endpoint: str
    method: str
    status_code: int
    tokens_used: int
    response_time: int
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyQuotaResponse(BaseModel):
    """API密钥配额响应"""
    id: str
    api_key_id: str
    quota_type: str
    quota_limit: int
    quota_used: int
    quota_reset_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApiKeyListResponse(BaseModel):
    """API密钥列表响应"""
    api_keys: List[ApiKeyResponse]
    total: int


class ApiKeyUsageListResponse(BaseModel):
    """API密钥使用记录列表响应"""
    usage_records: List[ApiKeyUsageResponse]
    total: int


class ApiKeyQuotaListResponse(BaseModel):
    """API密钥配额列表响应"""
    quotas: List[ApiKeyQuotaResponse]


# 外部API请求模式
class ExternalQueryRequest(BaseModel):
    """外部API知识库问答请求"""
    message: str = Field(..., description="用户问题")
    kb_ids: Optional[List[str]] = Field(None, description="指定知识库ID列表")
    model_id: Optional[str] = Field(None, description="指定模型ID")
    session_id: Optional[str] = Field(None, description="会话ID")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="高级参数"
    )
    stream: Optional[bool] = Field(False, description="是否启用流式响应")


class ExternalSearchRequest(BaseModel):
    """外部API向量检索请求"""
    query: str = Field(..., description="检索查询")
    kb_ids: Optional[List[str]] = Field(None, description="指定知识库ID列表")
    top_k: Optional[int] = Field(10, description="返回结果数量")
    similarity_threshold: Optional[float] = Field(0.7, description="相似度阈值")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="过滤条件"
    )


class ExternalHybridRequest(BaseModel):
    """外部API混合检索请求"""
    query: str = Field(..., description="检索查询")
    search_config: Dict[str, Any] = Field(
        default_factory=lambda: {
            "vector_weight": 0.7,
            "keyword_weight": 0.3,
            "top_k": 10
        },
        description="检索配置"
    )
    kb_ids: Optional[List[str]] = Field(None, description="指定知识库ID列表")
    similarity_threshold: Optional[float] = Field(0.7, description="相似度阈值")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="过滤条件"
    )


# 外部API响应模式
class ExternalQueryResponse(BaseModel):
    """外部API知识库问答响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ExternalSearchResponse(BaseModel):
    """外部API向量检索响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ExternalHybridResponse(BaseModel):
    """外部API混合检索响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ExternalKbInfoResponse(BaseModel):
    """外部API知识库信息响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class ExternalKbListResponse(BaseModel):
    """外部API知识库列表响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None 