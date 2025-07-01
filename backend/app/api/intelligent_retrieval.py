"""
智能检索API路由
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import logging

from ..services.intelligent_retrieval_service import IntelligentRetrievalService
from ..services.vector_service import VectorService
from ..services.hybrid_retriever import HybridRetriever
from ..services.enhanced_retrieval_pipeline import EnhancedRetrievalPipeline
from ..core.database import get_db
from ..schemas.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/intelligent-retrieval", tags=["智能检索"])

# 全局智能检索服务实例
intelligent_service: Optional[IntelligentRetrievalService] = None


class IntelligentSearchRequest(BaseModel):
    """智能检索请求"""
    query: str
    kb_ids: List[str]
    user_context: Optional[Dict[str, Any]] = None
    force_strategy: Optional[str] = None
    enable_learning: bool = True
    timeout_ms: Optional[int] = None


class IntelligentSearchResponse(BaseModel):
    """智能检索响应"""
    success: bool
    data: Dict[str, Any]
    message: str


class StrategyRecommendationRequest(BaseModel):
    """策略推荐请求"""
    query: str
    user_context: Optional[Dict[str, Any]] = None


class StrategyRecommendationResponse(BaseModel):
    """策略推荐响应"""
    success: bool
    data: List[Dict[str, Any]]
    message: str


def get_intelligent_service() -> IntelligentRetrievalService:
    """获取智能检索服务实例"""
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


@router.post("/search", response_model=IntelligentSearchResponse)
async def intelligent_search(
    request: IntelligentSearchRequest,
    current_user = Depends(get_current_user)
):
    """智能检索接口"""
    try:
        service = get_intelligent_service()
        
        # 构建用户上下文
        user_context = request.user_context or {}
        user_context.update({
            "user_id": str(current_user.id),
            "user_level": current_user.role,
            "preferences": getattr(current_user, 'preferences', {})
        })
        
        # 执行智能检索
        result = await service.intelligent_search(
            query=request.query,
            kb_ids=request.kb_ids,
            user_context=user_context,
            force_strategy=request.force_strategy,
            enable_learning=request.enable_learning
        )
        
        return IntelligentSearchResponse(
            success=result["success"],
            data=result["data"],
            message=result["message"]
        )
        
    except Exception as e:
        logger.error(f"智能检索失败: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/recommend-strategy", response_model=StrategyRecommendationResponse)
async def recommend_strategy(
    request: StrategyRecommendationRequest,
    current_user = Depends(get_current_user)
):
    """策略推荐接口"""
    try:
        service = get_intelligent_service()
        
        # 获取策略推荐
        recommendations = service.get_strategy_recommendations(request.query)
        
        return StrategyRecommendationResponse(
            success=True,
            data=recommendations,
            message="策略推荐成功"
        )
        
    except Exception as e:
        logger.error(f"策略推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


@router.get("/stats", response_model=IntelligentSearchResponse)
async def get_intelligent_retrieval_stats(
    current_user = Depends(get_current_user)
):
    """获取智能检索统计信息"""
    try:
        service = get_intelligent_service()
        stats = service.get_stats()
        
        return IntelligentSearchResponse(
            success=True,
            data=stats,
            message="获取统计信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.get("/health", response_model=IntelligentSearchResponse)
async def health_check():
    """健康检查"""
    try:
        service = get_intelligent_service()
        
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
        
        return IntelligentSearchResponse(
            success=all_healthy,
            data={
                "status": "healthy" if all_healthy else "unhealthy",
                "services": health_status,
                "total_queries": service.stats["total_queries"],
                "avg_response_time": service.stats["avg_response_time"]
            },
            message="服务正常" if all_healthy else "服务异常"
        )
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return IntelligentSearchResponse(
            success=False,
            data={"status": "error", "error": str(e)},
            message="健康检查失败"
        ) 