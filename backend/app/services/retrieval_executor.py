"""
检索执行器
"""
from typing import List, Dict, Any, Optional
import asyncio
import logging

from .strategy_scheduler import RetrievalStrategy, ServiceType
from .vector_service import VectorService
from .hybrid_retriever import HybridRetriever
from .enhanced_retrieval_pipeline import EnhancedRetrievalPipeline

logger = logging.getLogger(__name__)

class RetrievalExecutor:
    def __init__(self):
        self.vector_service = None
        self.hybrid_retriever = None
        self.enhanced_pipeline = None
    
    def set_services(self, vector_service: VectorService = None,
                    hybrid_retriever: HybridRetriever = None,
                    enhanced_pipeline: EnhancedRetrievalPipeline = None):
        self.vector_service = vector_service
        self.hybrid_retriever = hybrid_retriever
        self.enhanced_pipeline = enhanced_pipeline
    
    async def execute(self, strategy: RetrievalStrategy, query: str, 
                     kb_ids: List[str], user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            if strategy.service_type == ServiceType.VECTOR:
                return await self._execute_vector_search(strategy, query, kb_ids)
            elif strategy.service_type == ServiceType.HYBRID:
                return await self._execute_hybrid_search(strategy, query, kb_ids)
            elif strategy.service_type == ServiceType.ENHANCED:
                return await self._execute_enhanced_search(strategy, query, kb_ids, user_context)
            elif strategy.service_type == ServiceType.KEYWORD:
                return await self._execute_keyword_search(strategy, query, kb_ids)
            else:
                return await self._execute_fallback_search(strategy, query, kb_ids)
        except Exception as e:
            logger.error(f"检索执行失败: {e}")
            return await self._execute_fallback_search(strategy, query, kb_ids)
    
    async def _execute_vector_search(self, strategy: RetrievalStrategy, 
                                   query: str, kb_ids: List[str]) -> Dict[str, Any]:
        if not self.vector_service:
            raise Exception("向量服务未初始化")
        
        top_k = strategy.parameters.get("top_k", 10)
        similarity_threshold = strategy.parameters.get("similarity_threshold", 0.7)
        
        results = await self.vector_service.search_text(query, kb_ids, top_k)
        
        # 过滤相似度阈值
        filtered_results = [
            result for result in results 
            if result.get("score", 0) >= similarity_threshold
        ]
        
        return {
            "results": filtered_results,
            "strategy_info": {
                "service_type": "vector",
                "parameters_used": strategy.parameters,
                "results_count": len(filtered_results)
            }
        }
    
    async def _execute_hybrid_search(self, strategy: RetrievalStrategy, 
                                   query: str, kb_ids: List[str]) -> Dict[str, Any]:
        if not self.hybrid_retriever:
            raise Exception("混合检索器未初始化")
        
        top_k = strategy.parameters.get("top_k", 10)
        vector_weight = strategy.parameters.get("vector_weight", 0.7)
        keyword_weight = strategy.parameters.get("keyword_weight", 0.3)
        
        # 更新权重
        self.hybrid_retriever.weights = {
            "vector": vector_weight,
            "keyword": keyword_weight
        }
        
        results = await self.hybrid_retriever.retrieve(query, kb_ids, top_k)
        
        return {
            "results": results,
            "strategy_info": {
                "service_type": "hybrid",
                "parameters_used": strategy.parameters,
                "results_count": len(results)
            }
        }
    
    async def _execute_enhanced_search(self, strategy: RetrievalStrategy, 
                                     query: str, kb_ids: List[str], 
                                     user_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.enhanced_pipeline:
            raise Exception("增强检索流水线未初始化")
        
        # 更新流水线配置
        from .enhanced_retrieval_pipeline import PipelineConfig
        config = PipelineConfig(
            enable_query_expansion=strategy.parameters.get("enable_expansion", True),
            enable_reranking=strategy.parameters.get("enable_rerank", True),
            final_top_k=strategy.parameters.get("top_k", 10)
        )
        self.enhanced_pipeline.update_config(config)
        
        # 执行增强检索
        result = await self.enhanced_pipeline.retrieve(query, kb_ids, user_context)
        
        return {
            "results": result.final_documents,
            "strategy_info": {
                "service_type": "enhanced",
                "parameters_used": strategy.parameters,
                "results_count": len(result.final_documents),
                "pipeline_stats": result.pipeline_stats
            }
        }
    
    async def _execute_keyword_search(self, strategy: RetrievalStrategy, 
                                    query: str, kb_ids: List[str]) -> Dict[str, Any]:
        # 简单的关键词搜索实现
        if not self.vector_service:
            raise Exception("向量服务未初始化")
        
        top_k = strategy.parameters.get("top_k", 10)
        priority_keywords = strategy.parameters.get("priority_keywords", [])
        
        # 使用向量服务进行基础搜索
        results = await self.vector_service.search_text(query, kb_ids, top_k * 2)
        
        # 简单的关键词匹配评分
        scored_results = []
        for result in results:
            content = result.get("content", "").lower()
            score = result.get("score", 0)
            
            # 检查优先级关键词
            keyword_bonus = 0
            for keyword in priority_keywords:
                if keyword.lower() in content:
                    keyword_bonus += 0.1
            
            # 调整分数
            adjusted_score = min(1.0, score + keyword_bonus)
            scored_results.append({
                **result,
                "score": adjusted_score,
                "keyword_bonus": keyword_bonus
            })
        
        # 按调整后的分数排序
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "results": scored_results[:top_k],
            "strategy_info": {
                "service_type": "keyword",
                "parameters_used": strategy.parameters,
                "results_count": len(scored_results[:top_k])
            }
        }
    
    async def _execute_fallback_search(self, strategy: RetrievalStrategy, 
                                     query: str, kb_ids: List[str]) -> Dict[str, Any]:
        logger.warning("使用降级检索")
        
        if self.vector_service:
            try:
                results = await self.vector_service.search_text(query, kb_ids, 5)
                return {
                    "results": results,
                    "strategy_info": {
                        "service_type": "fallback",
                        "parameters_used": {"top_k": 5},
                        "results_count": len(results)
                    }
                }
            except Exception as e:
                logger.error(f"降级检索失败: {e}")
        
        return {
            "results": [],
            "strategy_info": {
                "service_type": "fallback",
                "parameters_used": {},
                "results_count": 0
            }
        } 