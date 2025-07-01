"""
智能检索服务
自动识别用户查询意图，选择最合适的检索策略
"""
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum

from .intent_recognizer import IntentRecognizer, IntentInfo
from .strategy_scheduler import StrategyScheduler, RetrievalStrategy
from .retrieval_executor import RetrievalExecutor
from .vector_service import VectorService
from .hybrid_retriever import HybridRetriever
from .enhanced_retrieval_pipeline import EnhancedRetrievalPipeline

logger = logging.getLogger(__name__)


class IntelligentRetrievalService:
    """智能检索服务"""
    
    def __init__(self, db=None):
        self.db = db
        
        # 初始化核心组件
        self.intent_recognizer = IntentRecognizer()
        self.strategy_scheduler = StrategyScheduler()
        self.retrieval_executor = RetrievalExecutor()
        
        # 初始化检索服务
        self.vector_service = VectorService(db) if db else None
        self.hybrid_retriever = HybridRetriever(self.vector_service) if self.vector_service else None
        self.enhanced_pipeline = EnhancedRetrievalPipeline(self.vector_service) if self.vector_service else None
        
        # 统计信息
        self.stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "strategy_usage": {},
            "intent_distribution": {}
        }
    
    async def intelligent_search(
        self, 
        query: str, 
        kb_ids: List[str], 
        user_context: Optional[Dict[str, Any]] = None,
        force_strategy: Optional[str] = None,
        enable_learning: bool = True
    ) -> Dict[str, Any]:
        """智能检索主入口"""
        start_time = time.time()
        
        try:
            logger.info(f"开始智能检索，查询: {query}")
            
            # 1. 意图识别
            intent = await self.intent_recognizer.recognize_intent(query, user_context or {})
            
            # 2. 策略选择
            if force_strategy:
                strategy = self.strategy_scheduler.get_strategy_by_name(force_strategy)
            else:
                strategy = await self.strategy_scheduler.select_strategy(intent)
            
            # 3. 检索执行
            retrieval_result = await self.retrieval_executor.execute(
                strategy, query, kb_ids, user_context
            )
            
            # 4. 计算性能指标
            processing_time = time.time() - start_time
            performance_metrics = {
                "response_time": processing_time,
                "strategy_used": strategy.strategy_name,
                "intent_confidence": intent.confidence,
                "results_count": len(retrieval_result.get("results", []))
            }
            
            # 5. 学习反馈
            if enable_learning:
                await self._learn_from_query(intent, strategy, performance_metrics)
            
            # 6. 更新统计
            self._update_stats(intent, strategy, processing_time, retrieval_result)
            
            # 7. 构建响应
            response = {
                "success": True,
                "data": {
                    "results": retrieval_result.get("results", []),
                    "strategy_used": {
                        "service_type": strategy.service_type,
                        "strategy_name": strategy.strategy_name,
                        "parameters": strategy.parameters,
                        "reasoning": strategy.reasoning
                    },
                    "intent_analysis": {
                        "query_type": intent.query_type.value,
                        "complexity": intent.complexity.value,
                        "confidence": intent.confidence,
                        "features": intent.features
                    },
                    "performance_metrics": performance_metrics
                },
                "message": "检索成功"
            }
            
            logger.info(f"智能检索完成，策略: {strategy.strategy_name}, 耗时: {processing_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"智能检索失败: {e}")
            processing_time = time.time() - start_time
            
            # 降级处理
            fallback_result = await self._fallback_search(query, kb_ids)
            
            return {
                "success": False,
                "data": {
                    "results": fallback_result.get("results", []),
                    "strategy_used": {
                        "service_type": "fallback",
                        "strategy_name": "降级检索",
                        "parameters": {},
                        "reasoning": f"智能检索失败，使用降级策略: {str(e)}"
                    },
                    "intent_analysis": {
                        "query_type": "unknown",
                        "complexity": "unknown",
                        "confidence": 0.0,
                        "features": {}
                    },
                    "performance_metrics": {
                        "response_time": processing_time,
                        "error": str(e)
                    }
                },
                "message": f"检索失败: {str(e)}"
            }
    
    async def _fallback_search(self, query: str, kb_ids: List[str]) -> Dict[str, Any]:
        """降级检索"""
        try:
            if self.vector_service:
                # 使用向量检索作为降级
                results = await self.vector_service.search_text(query, kb_ids, 5)
                return {"results": results}
            else:
                # 最简单的降级
                return {"results": []}
        except Exception as e:
            logger.error(f"降级检索也失败: {e}")
            return {"results": []}
    
    def _update_stats(self, intent: IntentInfo, strategy: RetrievalStrategy, 
                     processing_time: float, result: Dict[str, Any]):
        """更新统计信息"""
        self.stats["total_queries"] += 1
        
        if result.get("results"):
            self.stats["successful_queries"] += 1
        else:
            self.stats["failed_queries"] += 1
        
        # 更新平均响应时间
        total_time = self.stats["avg_response_time"] * (self.stats["total_queries"] - 1)
        total_time += processing_time
        self.stats["avg_response_time"] = total_time / self.stats["total_queries"]
        
        # 更新策略使用统计
        strategy_name = strategy.strategy_name
        if strategy_name not in self.stats["strategy_usage"]:
            self.stats["strategy_usage"][strategy_name] = 0
        self.stats["strategy_usage"][strategy_name] += 1
        
        # 更新意图分布统计
        query_type = intent.query_type.value
        if query_type not in self.stats["intent_distribution"]:
            self.stats["intent_distribution"][query_type] = 0
        self.stats["intent_distribution"][query_type] += 1
    
    async def _learn_from_query(self, intent: IntentInfo, strategy: RetrievalStrategy, 
                               performance_metrics: Dict[str, Any]):
        """从查询中学习"""
        # 这里应该实现学习逻辑
        # 例如：记录策略效果、更新用户偏好等
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
    
    def get_strategy_recommendations(self, query: str) -> List[Dict[str, Any]]:
        """获取策略推荐"""
        return [
            {
                "strategy": "vector",
                "name": "向量检索",
                "description": "适合语义相关查询",
                "confidence": 0.8
            },
            {
                "strategy": "hybrid",
                "name": "混合检索",
                "description": "平衡精度和召回率",
                "confidence": 0.9
            },
            {
                "strategy": "enhanced",
                "name": "增强检索",
                "description": "最高精度，适合复杂查询",
                "confidence": 0.7
            }
        ]

class QueryClassifier:
    """查询分类器"""
    
    def __init__(self):
        # 查询类型关键词
        self.type_keywords = {
            QueryType.FACTUAL: [
                "什么是", "多少", "几", "何时", "哪里", "谁", "哪个", "原因", "定义", "介绍",
                "what is", "how many", "when", "where", "who", "which", "reason", "define", "introduction"
            ],
            QueryType.CONCEPTUAL: [
                "解释", "说明", "原理", "概念", "定义", "含义",
                "explain", "concept", "definition", "meaning", "principle"
            ],
            QueryType.PROCEDURAL: [
                "如何", "怎么", "步骤", "方法", "流程", "操作",
                "how to", "step", "method", "process", "procedure"
            ],
            QueryType.COMPARATIVE: [
                "比较", "区别", "差异", "vs", "versus", "对比",
                "compare", "difference", "versus", "vs"
            ],
            QueryType.TROUBLESHOOTING: [
                "错误", "问题", "故障", "失败", "解决", "修复",
                "error", "problem", "issue", "fix", "solve", "troubleshoot"
            ]
        } 