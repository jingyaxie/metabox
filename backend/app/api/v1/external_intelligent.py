"""
外部智能检索API接口
支持API密钥认证，无需用户登录和对话上下文
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
import time
import logging

from ...services.intelligent_retrieval_service import IntelligentRetrievalService
from ...services.vector_service import VectorService
from ...services.hybrid_retriever import HybridRetriever
from ...services.enhanced_retrieval_pipeline import EnhancedRetrievalPipeline
from ...core.database import get_db
from ...models.api_key import ApiKey
from ...core.auth import require_search_permission

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/intelligent", tags=["外部智能检索"])

# 全局智能检索服务实例
intelligent_service: Optional[IntelligentRetrievalService] = None


class ExternalIntelligentSearchRequest(BaseModel):
    """外部智能检索请求"""
    query: str = Field(..., description="检索查询")
    kb_ids: Optional[List[str]] = Field(None, description="指定知识库ID列表")
    user_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="用户上下文信息"
    )
    force_strategy: Optional[str] = Field(None, description="强制使用指定检索策略")
    enable_learning: bool = Field(True, description="是否启用学习功能")
    timeout_ms: Optional[int] = Field(None, description="超时时间(毫秒)")
    top_k: Optional[int] = Field(10, description="返回结果数量")
    similarity_threshold: Optional[float] = Field(0.7, description="相似度阈值")


class ExternalIntelligentSearchResponse(BaseModel):
    """外部智能检索响应"""
    success: bool
    data: Dict[str, Any]
    message: str


class ExternalStrategyRecommendationRequest(BaseModel):
    """外部策略推荐请求"""
    query: str = Field(..., description="查询内容")
    user_context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="用户上下文信息"
    )


class ExternalStrategyRecommendationResponse(BaseModel):
    """外部策略推荐响应"""
    success: bool
    data: List[Dict[str, Any]]
    message: str


def get_external_intelligent_service() -> IntelligentRetrievalService:
    """获取外部智能检索服务实例"""
    global intelligent_service
    if intelligent_service is None:
        db = next(get_db())
        vector_service = VectorService(db)
        hybrid_retriever = HybridRetriever(vector_service)
        enhanced_pipeline = EnhancedRetrievalPipeline(vector_service)
        
        intelligent_service = IntelligentRetrievalService(db)
        intelligent_service.vector_service = vector_service
        intelligent_service.hybrid_retriever = hybrid_retriever
        intelligent_service.enhanced_pipeline = enhanced_pipeline
        
        # 设置检索执行器的服务
        intelligent_service.retrieval_executor.set_services(
            vector_service=vector_service,
            hybrid_retriever=hybrid_retriever,
            enhanced_pipeline=enhanced_pipeline
        )
    
    return intelligent_service


@router.post("/search", response_model=ExternalIntelligentSearchResponse)
async def external_intelligent_search(
    request: ExternalIntelligentSearchRequest,
    api_request: Request,
    api_key: ApiKey = Depends(require_search_permission()),
    db = Depends(get_db)
):
    """外部API智能检索接口"""
    start_time = time.time()
    
    try:
        # 检查知识库访问权限
        if request.kb_ids:
            for kb_id in request.kb_ids:
                if not api_key.has_permission("search", kb_id):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "success": False,
                            "error": {
                                "code": "KB_ACCESS_DENIED",
                                "message": f"没有访问知识库 {kb_id} 的权限"
                            }
                        }
                    )
        
        # 获取智能检索服务
        service = get_external_intelligent_service()
        
        # 构建用户上下文（外部API场景）
        user_context = request.user_context or {}
        user_context.update({
            "api_key_id": str(api_key.id),
            "user_level": "external",
            "source": "external_api",
            "preferences": {
                "response_speed": "balanced",
                "quality_priority": "high"
            }
        })
        
        # 执行智能检索
        result = await service.intelligent_search(
            query=request.query,
            kb_ids=request.kb_ids or [],
            user_context=user_context,
            force_strategy=request.force_strategy,
            enable_learning=request.enable_learning
        )
        
        # 应用top_k和similarity_threshold过滤
        if result["success"] and result["data"].get("results"):
            results = result["data"]["results"]
            
            # 相似度过滤
            if request.similarity_threshold:
                results = [
                    r for r in results 
                    if r.get("score", 0) >= request.similarity_threshold
                ]
            
            # 数量限制
            if request.top_k:
                results = results[:request.top_k]
            
            result["data"]["results"] = results
            result["data"]["total"] = len(results)
        
        # 记录使用情况
        response_time = int((time.time() - start_time) * 1000)
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=200,
            tokens_used=0,
            db=db
        )
        
        return ExternalIntelligentSearchResponse(
            success=result["success"],
            data={
                **result["data"],
                "query_time": response_time,
                "api_key_id": str(api_key.id)
            },
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"外部智能检索失败: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"检索失败: {str(e)}"
                }
            }
        )


@router.post("/recommend-strategy", response_model=ExternalStrategyRecommendationResponse)
async def external_recommend_strategy(
    request: ExternalStrategyRecommendationRequest,
    api_request: Request,
    api_key: ApiKey = Depends(require_search_permission()),
    db = Depends(get_db)
):
    """外部API策略推荐接口"""
    try:
        service = get_external_intelligent_service()
        
        # 获取策略推荐
        recommendations = service.get_strategy_recommendations(request.query)
        
        # 记录使用情况
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=200,
            tokens_used=0,
            db=db
        )
        
        return ExternalStrategyRecommendationResponse(
            success=True,
            data=recommendations,
            message="策略推荐成功"
        )
        
    except Exception as e:
        logger.error(f"外部策略推荐失败: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": f"推荐失败: {str(e)}"
                }
            }
        )


@router.get("/health", response_model=ExternalIntelligentSearchResponse)
async def external_health_check():
    """外部API健康检查"""
    try:
        service = get_external_intelligent_service()
        
        # 检查各个服务是否正常
        health_status = {
            "vector_service": service.vector_service is not None,
            "hybrid_retriever": service.hybrid_retriever is not None,
            "enhanced_pipeline": service.enhanced_pipeline is not None,
            "intent_recognizer": service.intent_recognizer is not None,
            "strategy_scheduler": service.strategy_scheduler is not None,
            "retrieval_executor": service.retrieval_executor is not None
        }
        
        all_healthy = all(health_status.values())
        
        return ExternalIntelligentSearchResponse(
            success=all_healthy,
            data={
                "status": "healthy" if all_healthy else "unhealthy",
                "services": health_status,
                "total_queries": service.stats["total_queries"],
                "avg_response_time": service.stats["avg_response_time"],
                "strategy_usage": service.stats["strategy_usage"],
                "intent_distribution": service.stats["intent_distribution"]
            },
            message="服务正常" if all_healthy else "服务异常"
        )
        
    except Exception as e:
        logger.error(f"外部健康检查失败: {e}")
        return ExternalIntelligentSearchResponse(
            success=False,
            data={"status": "error", "error": str(e)},
            message="健康检查失败"
        ) 