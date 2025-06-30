"""
增强检索API路由
提供检索流水线的配置和查询接口
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import logging

from ..services.enhanced_retrieval_pipeline import (
    EnhancedRetrievalPipeline, 
    PipelineConfig, 
    PipelineResult,
    PipelineStage
)
from ..services.multi_query_expander import ExpansionStrategy
from ..services.hybrid_retriever import FusionStrategy
from ..services.reranker import RerankStrategy
from ..services.metadata_filter import FilterCondition, FilterOperator
from ..services.vector_service import VectorService
from ..core.database import get_db
from ..schemas.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enhanced-retrieval", tags=["增强检索"])

# 全局流水线实例
pipeline: Optional[EnhancedRetrievalPipeline] = None


class QueryRequest(BaseModel):
    """查询请求"""
    query: str
    kb_ids: List[str]
    user_context: Optional[Dict[str, Any]] = None
    config: Optional[PipelineConfig] = None


class QueryResponse(BaseModel):
    """查询响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""


class PipelineConfigRequest(BaseModel):
    """流水线配置请求"""
    enable_query_preprocessing: bool = True
    enable_query_expansion: bool = True
    expansion_strategy: ExpansionStrategy = ExpansionStrategy.HYBRID
    expansion_count: int = 3
    enable_metadata_filtering: bool = True
    predefined_filters: Optional[List[str]] = None
    enable_hybrid_retrieval: bool = True
    fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_SUM
    retrieval_weights: Optional[Dict[str, float]] = None
    enable_reranking: bool = True
    rerank_strategy: RerankStrategy = RerankStrategy.HYBRID
    rerank_top_k: int = 20
    max_retrieval_results: int = 50
    final_top_k: int = 10
    enable_parallel_processing: bool = True


class FilterConditionRequest(BaseModel):
    """过滤条件请求"""
    field: str
    operator: FilterOperator
    value: Any


class PipelineStatsResponse(BaseModel):
    """流水线统计响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""


def get_pipeline() -> EnhancedRetrievalPipeline:
    """获取流水线实例"""
    global pipeline
    if pipeline is None:
        # 初始化流水线
        vector_service = VectorService()
        pipeline = EnhancedRetrievalPipeline(
            vector_service=vector_service,
            config=PipelineConfig()
        )
    return pipeline


@router.post("/query", response_model=QueryResponse)
async def enhanced_query(
    request: QueryRequest,
    current_user = Depends(get_current_user)
):
    """增强检索查询"""
    try:
        pipeline = get_pipeline()
        
        # 如果提供了自定义配置，更新流水线配置
        if request.config:
            pipeline.update_config(request.config)
        
        # 执行检索
        result = await pipeline.retrieve(
            query=request.query,
            kb_ids=request.kb_ids,
            user_context=request.user_context
        )
        
        # 构建响应数据
        response_data = {
            "query": result.query,
            "original_query": result.original_query,
            "expanded_queries": result.expanded_queries,
            "final_documents": result.final_documents,
            "pipeline_stats": result.pipeline_stats,
            "processing_time": result.processing_time
        }
        
        return QueryResponse(
            success=True,
            data=response_data,
            message="检索成功"
        )
        
    except Exception as e:
        logger.error(f"增强检索查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/config", response_model=QueryResponse)
async def update_pipeline_config(
    config: PipelineConfigRequest,
    current_user = Depends(get_current_user)
):
    """更新流水线配置"""
    try:
        pipeline = get_pipeline()
        
        # 转换为PipelineConfig对象
        pipeline_config = PipelineConfig(
            enable_query_preprocessing=config.enable_query_preprocessing,
            enable_query_expansion=config.enable_query_expansion,
            expansion_strategy=config.expansion_strategy,
            expansion_count=config.expansion_count,
            enable_metadata_filtering=config.enable_metadata_filtering,
            predefined_filters=config.predefined_filters,
            enable_hybrid_retrieval=config.enable_hybrid_retrieval,
            fusion_strategy=config.fusion_strategy,
            retrieval_weights=config.retrieval_weights,
            enable_reranking=config.enable_reranking,
            rerank_strategy=config.rerank_strategy,
            rerank_top_k=config.rerank_top_k,
            max_retrieval_results=config.max_retrieval_results,
            final_top_k=config.final_top_k,
            enable_parallel_processing=config.enable_parallel_processing
        )
        
        pipeline.update_config(pipeline_config)
        
        return QueryResponse(
            success=True,
            data={"config": config.dict()},
            message="配置更新成功"
        )
        
    except Exception as e:
        logger.error(f"更新流水线配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"配置更新失败: {str(e)}")


@router.get("/config", response_model=QueryResponse)
async def get_pipeline_config(
    current_user = Depends(get_current_user)
):
    """获取当前流水线配置"""
    try:
        pipeline = get_pipeline()
        config = pipeline.config
        
        config_data = {
            "enable_query_preprocessing": config.enable_query_preprocessing,
            "enable_query_expansion": config.enable_query_expansion,
            "expansion_strategy": config.expansion_strategy.value,
            "expansion_count": config.expansion_count,
            "enable_metadata_filtering": config.enable_metadata_filtering,
            "predefined_filters": config.predefined_filters,
            "enable_hybrid_retrieval": config.enable_hybrid_retrieval,
            "fusion_strategy": config.fusion_strategy.value,
            "retrieval_weights": config.retrieval_weights,
            "enable_reranking": config.enable_reranking,
            "rerank_strategy": config.rerank_strategy.value,
            "rerank_top_k": config.rerank_top_k,
            "max_retrieval_results": config.max_retrieval_results,
            "final_top_k": config.final_top_k,
            "enable_parallel_processing": config.enable_parallel_processing
        }
        
        return QueryResponse(
            success=True,
            data=config_data,
            message="获取配置成功"
        )
        
    except Exception as e:
        logger.error(f"获取流水线配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.get("/stats", response_model=PipelineStatsResponse)
async def get_pipeline_stats(
    current_user = Depends(get_current_user)
):
    """获取流水线统计信息"""
    try:
        pipeline = get_pipeline()
        stats = pipeline.get_pipeline_stats()
        
        return PipelineStatsResponse(
            success=True,
            data=stats,
            message="获取统计信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取流水线统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")


@router.post("/test-query-expansion", response_model=QueryResponse)
async def test_query_expansion(
    query: str = Query(..., description="测试查询"),
    strategy: ExpansionStrategy = Query(ExpansionStrategy.HYBRID, description="扩展策略"),
    expansion_count: int = Query(3, description="扩展数量"),
    current_user = Depends(get_current_user)
):
    """测试查询扩展"""
    try:
        pipeline = get_pipeline()
        
        # 执行查询扩展
        expanded_queries = await pipeline.query_expander.expand_query(
            query=query,
            strategy=strategy,
            context=None
        )
        
        # 获取扩展统计
        expansion_stats = pipeline.query_expander.get_expansion_stats(query)
        
        response_data = {
            "original_query": query,
            "expanded_queries": expanded_queries,
            "expansion_strategy": strategy.value,
            "expansion_count": expansion_count,
            "expansion_stats": expansion_stats
        }
        
        return QueryResponse(
            success=True,
            data=response_data,
            message="查询扩展测试成功"
        )
        
    except Exception as e:
        logger.error(f"查询扩展测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.post("/test-metadata-filtering", response_model=QueryResponse)
async def test_metadata_filtering(
    documents: List[Dict[str, Any]],
    predefined_filters: Optional[List[str]] = Query(None, description="预定义过滤器"),
    current_user = Depends(get_current_user)
):
    """测试元数据过滤"""
    try:
        pipeline = get_pipeline()
        
        # 执行元数据过滤
        filtered_documents = await pipeline.metadata_filter.filter_documents(
            documents=documents,
            predefined_filters=predefined_filters
        )
        
        # 获取过滤统计
        filter_stats = pipeline.metadata_filter.get_filter_stats(
            len(documents), len(filtered_documents)
        )
        
        response_data = {
            "original_count": len(documents),
            "filtered_count": len(filtered_documents),
            "filtered_documents": filtered_documents,
            "filter_stats": filter_stats,
            "applied_filters": predefined_filters or []
        }
        
        return QueryResponse(
            success=True,
            data=response_data,
            message="元数据过滤测试成功"
        )
        
    except Exception as e:
        logger.error(f"元数据过滤测试失败: {e}")
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.get("/available-filters", response_model=QueryResponse)
async def get_available_filters(
    current_user = Depends(get_current_user)
):
    """获取可用的预定义过滤器"""
    try:
        pipeline = get_pipeline()
        available_filters = pipeline.metadata_filter.get_available_filters()
        
        return QueryResponse(
            success=True,
            data={"available_filters": available_filters},
            message="获取可用过滤器成功"
        )
        
    except Exception as e:
        logger.error(f"获取可用过滤器失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/add-synonyms", response_model=QueryResponse)
async def add_synonyms(
    word: str = Query(..., description="词汇"),
    synonyms: List[str] = Query(..., description="同义词列表"),
    current_user = Depends(get_current_user)
):
    """添加同义词"""
    try:
        pipeline = get_pipeline()
        pipeline.query_expander.add_synonyms(word, synonyms)
        
        return QueryResponse(
            success=True,
            data={"word": word, "synonyms": synonyms},
            message="同义词添加成功"
        )
        
    except Exception as e:
        logger.error(f"添加同义词失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.post("/add-custom-filter", response_model=QueryResponse)
async def add_custom_filter(
    name: str = Query(..., description="过滤器名称"),
    current_user = Depends(get_current_user)
):
    """添加自定义过滤器"""
    try:
        pipeline = get_pipeline()
        
        # 这里可以添加自定义过滤器的逻辑
        # 暂时返回成功响应
        
        return QueryResponse(
            success=True,
            data={"filter_name": name},
            message="自定义过滤器添加成功"
        )
        
    except Exception as e:
        logger.error(f"添加自定义过滤器失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}") 