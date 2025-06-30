"""
智能配置相关的数据模式
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class DocumentType(str, Enum):
    """文档类型枚举"""
    CODE = "code"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    NEWS = "news"
    LITERATURE = "literature"
    GENERAL = "general"
    MARKDOWN = "markdown"
    MANUAL = "manual"


class ParameterRecommendation(BaseModel):
    """参数推荐"""
    chunk_size: int = Field(..., description="分块大小")
    chunk_overlap: int = Field(..., description="重叠大小")
    embedding_model: str = Field(..., description="Embedding模型")
    similarity_threshold: float = Field(..., description="相似度阈值")
    max_tokens: int = Field(..., description="最大token数")
    reasoning: str = Field(..., description="推荐理由")
    splitter_type: Optional[str] = Field("recursive", description="分割器类型")
    use_parent_child: Optional[bool] = Field(False, description="是否使用父子块分割")
    parent_chunk_size: Optional[int] = Field(None, description="父块大小")
    child_chunk_size: Optional[int] = Field(None, description="子块大小")


class ValidationResult(BaseModel):
    """验证结果"""
    is_valid: bool = Field(..., description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    warnings: List[str] = Field(default_factory=list, description="警告信息")


class SmartConfigRequest(BaseModel):
    """智能配置请求"""
    content: str = Field(..., description="待分析的文档内容")
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="用户自定义参数")


class SmartConfigResponse(BaseModel):
    """智能配置响应"""
    document_type: DocumentType = Field(..., description="检测到的文档类型")
    content_length: int = Field(..., description="内容长度")
    recommendation: ParameterRecommendation = Field(..., description="参数推荐")
    validation: ValidationResult = Field(..., description="验证结果")
    confidence: float = Field(..., description="类型置信度")


class ConfigTemplate(BaseModel):
    """配置模板"""
    id: Optional[str] = Field(None, description="模板ID")
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    document_type: DocumentType = Field(..., description="适用文档类型")
    config: Dict[str, Any] = Field(..., description="配置参数")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")


class ConfigTemplateCreate(BaseModel):
    """创建配置模板"""
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    document_type: DocumentType = Field(..., description="适用文档类型")
    config: Dict[str, Any] = Field(..., description="配置参数")


class ConfigTemplateUpdate(BaseModel):
    """更新配置模板"""
    name: Optional[str] = Field(None, description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    document_type: Optional[DocumentType] = Field(None, description="适用文档类型")
    config: Optional[Dict[str, Any]] = Field(None, description="配置参数")


class BatchConfigRequest(BaseModel):
    """批量配置请求"""
    document_ids: List[str] = Field(..., description="文档ID列表")
    template_id: Optional[str] = Field(None, description="模板ID")
    config: Optional[Dict[str, Any]] = Field(None, description="自定义配置")


class BatchConfigResponse(BaseModel):
    """批量配置响应"""
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    errors: List[str] = Field(default_factory=list, description="错误信息")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="详细结果")


class PerformanceMetrics(BaseModel):
    """性能指标"""
    processing_time: float = Field(..., description="处理时间(秒)")
    memory_usage: float = Field(..., description="内存使用(MB)")
    storage_estimate: float = Field(..., description="存储预估(MB)")
    vector_count: int = Field(..., description="向量数量")
    chunk_count: int = Field(..., description="分块数量")


class ConfigPreview(BaseModel):
    """配置预览"""
    chunks: List[str] = Field(..., description="分块预览")
    chunk_count: int = Field(..., description="分块数量")
    avg_chunk_size: float = Field(..., description="平均分块大小")
    performance_metrics: PerformanceMetrics = Field(..., description="性能指标")
    quality_score: float = Field(..., description="质量评分")


class AdvancedConfig(BaseModel):
    """高级配置"""
    separators: List[str] = Field(default_factory=list, description="分隔符列表")
    header_levels: List[int] = Field(default_factory=list, description="标题层级")
    semantic_threshold: float = Field(0.8, description="语义阈值")
    parent_child_ratio: float = Field(0.3, description="父子块比例")
    max_parent_size: int = Field(2048, description="最大父块大小")
    min_child_size: int = Field(128, description="最小子块大小")
    overlap_strategy: str = Field("fixed", description="重叠策略")
    quality_metrics: List[str] = Field(default_factory=list, description="质量指标") 