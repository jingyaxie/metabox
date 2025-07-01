"""
策略调度器
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio

from .intent_recognizer import IntentInfo, QueryType, Complexity

class ServiceType(str, Enum):
    VECTOR = "vector"
    HYBRID = "hybrid"
    ENHANCED = "enhanced"
    KEYWORD = "keyword"
    FALLBACK = "fallback"

@dataclass
class RetrievalStrategy:
    service_type: ServiceType
    strategy_name: str
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float = 0.0

class StrategyRules:
    def __init__(self):
        self.rules = [
            # 事实查询规则
            {
                "condition": {"query_type": QueryType.FACTUAL, "complexity": Complexity.SIMPLE},
                "action": {
                    "service_type": ServiceType.VECTOR,
                    "strategy_name": "向量检索",
                    "parameters": {"top_k": 5, "similarity_threshold": 0.8},
                    "reasoning": "简单事实查询，使用向量检索快速响应"
                }
            },
            {
                "condition": {"query_type": QueryType.FACTUAL, "complexity": Complexity.COMPLEX},
                "action": {
                    "service_type": ServiceType.HYBRID,
                    "strategy_name": "混合检索",
                    "parameters": {"vector_weight": 0.8, "keyword_weight": 0.2, "top_k": 10},
                    "reasoning": "复杂事实查询，使用混合检索提高精度"
                }
            },
            # 概念查询规则
            {
                "condition": {"query_type": QueryType.CONCEPTUAL, "complexity": Complexity.SIMPLE},
                "action": {
                    "service_type": ServiceType.HYBRID,
                    "strategy_name": "混合检索",
                    "parameters": {"vector_weight": 0.7, "keyword_weight": 0.3, "top_k": 8},
                    "reasoning": "简单概念查询，使用混合检索平衡精度和效率"
                }
            },
            {
                "condition": {"query_type": QueryType.CONCEPTUAL, "complexity": Complexity.COMPLEX},
                "action": {
                    "service_type": ServiceType.ENHANCED,
                    "strategy_name": "增强检索流水线",
                    "parameters": {"enable_expansion": True, "enable_rerank": True, "top_k": 15},
                    "reasoning": "复杂概念查询，使用增强流水线获得最佳效果"
                }
            },
            # 程序查询规则
            {
                "condition": {"query_type": QueryType.PROCEDURAL, "complexity": Complexity.SIMPLE},
                "action": {
                    "service_type": ServiceType.KEYWORD,
                    "strategy_name": "关键词检索",
                    "parameters": {"top_k": 6, "priority_keywords": ["步骤", "方法", "how"]},
                    "reasoning": "简单程序查询，使用关键词检索匹配操作步骤"
                }
            },
            {
                "condition": {"query_type": QueryType.PROCEDURAL, "complexity": Complexity.COMPLEX},
                "action": {
                    "service_type": ServiceType.HYBRID,
                    "strategy_name": "混合检索",
                    "parameters": {"vector_weight": 0.6, "keyword_weight": 0.4, "top_k": 12},
                    "reasoning": "复杂程序查询，使用混合检索提高步骤匹配精度"
                }
            },
            # 比较查询规则
            {
                "condition": {"query_type": QueryType.COMPARATIVE},
                "action": {
                    "service_type": ServiceType.ENHANCED,
                    "strategy_name": "增强检索流水线",
                    "parameters": {"enable_expansion": True, "enable_rerank": True, "top_k": 20},
                    "reasoning": "比较查询需要多角度信息，使用增强流水线"
                }
            },
            # 故障查询规则
            {
                "condition": {"query_type": QueryType.TROUBLESHOOTING, "complexity": Complexity.SIMPLE},
                "action": {
                    "service_type": ServiceType.KEYWORD,
                    "strategy_name": "关键词检索",
                    "parameters": {"top_k": 5, "priority_keywords": ["错误", "问题", "解决"]},
                    "reasoning": "简单故障查询，使用关键词检索匹配错误信息"
                }
            },
            {
                "condition": {"query_type": QueryType.TROUBLESHOOTING, "complexity": Complexity.COMPLEX},
                "action": {
                    "service_type": ServiceType.HYBRID,
                    "strategy_name": "混合检索",
                    "parameters": {"vector_weight": 0.5, "keyword_weight": 0.5, "top_k": 15},
                    "reasoning": "复杂故障查询，使用混合检索提高问题匹配精度"
                }
            },
            # 默认规则
            {
                "condition": {},
                "action": {
                    "service_type": ServiceType.VECTOR,
                    "strategy_name": "向量检索",
                    "parameters": {"top_k": 10, "similarity_threshold": 0.7},
                    "reasoning": "默认使用向量检索"
                }
            }
        ]
    
    def get_strategy(self, intent: IntentInfo) -> RetrievalStrategy:
        for rule in self.rules:
            if self._match_condition(rule["condition"], intent):
                action = rule["action"]
                return RetrievalStrategy(
                    service_type=ServiceType(action["service_type"]),
                    strategy_name=action["strategy_name"],
                    parameters=action["parameters"],
                    reasoning=action["reasoning"],
                    confidence=0.8
                )
        # 返回默认策略
        return RetrievalStrategy(
            service_type=ServiceType.VECTOR,
            strategy_name="向量检索",
            parameters={"top_k": 10, "similarity_threshold": 0.7},
            reasoning="默认策略",
            confidence=0.5
        )
    
    def _match_condition(self, condition: Dict[str, Any], intent: IntentInfo) -> bool:
        for key, value in condition.items():
            if key == "query_type" and intent.query_type != value:
                return False
            elif key == "complexity" and intent.complexity != value:
                return False
        return True

class PerformanceMonitor:
    def __init__(self):
        self.performance_history = {}
        self.strategy_performance = {}
    
    def get_adjustment(self, intent: IntentInfo) -> Dict[str, Any]:
        # 基于历史性能数据调整策略
        adjustment = {
            "time_constraint": "normal",
            "quality_priority": "balanced",
            "resource_usage": "normal"
        }
        
        # 根据复杂度调整
        if intent.complexity == Complexity.COMPLEX:
            adjustment["time_constraint"] = "relaxed"
            adjustment["quality_priority"] = "high"
        elif intent.complexity == Complexity.SIMPLE:
            adjustment["time_constraint"] = "strict"
            adjustment["quality_priority"] = "speed"
        
        return adjustment
    
    def record_performance(self, strategy_name: str, metrics: Dict[str, Any]):
        if strategy_name not in self.strategy_performance:
            self.strategy_performance[strategy_name] = []
        self.strategy_performance[strategy_name].append(metrics)

class AdaptiveSelector:
    def __init__(self):
        self.adaptation_rules = {
            "high_load": {
                "vector_weight": 0.8,
                "keyword_weight": 0.2,
                "enable_rerank": False
            },
            "low_quality": {
                "enable_rerank": True,
                "rerank_top_k": 30
            },
            "speed_priority": {
                "enable_expansion": False,
                "enable_rerank": False
            }
        }
    
    def optimize(self, base_strategy: RetrievalStrategy, 
                performance_adjustment: Dict[str, Any],
                intent: IntentInfo) -> RetrievalStrategy:
        optimized_strategy = RetrievalStrategy(
            service_type=base_strategy.service_type,
            strategy_name=base_strategy.strategy_name,
            parameters=base_strategy.parameters.copy(),
            reasoning=base_strategy.reasoning,
            confidence=base_strategy.confidence
        )
        
        # 根据性能调整优化参数
        if performance_adjustment.get("time_constraint") == "strict":
            optimized_strategy.parameters.update(self.adaptation_rules["speed_priority"])
            optimized_strategy.reasoning += " (速度优先)"
        
        elif performance_adjustment.get("quality_priority") == "high":
            optimized_strategy.parameters.update(self.adaptation_rules["low_quality"])
            optimized_strategy.reasoning += " (质量优先)"
        
        # 根据用户偏好调整
        if intent.user_profile:
            preferred_strategy = intent.user_profile.get("preferred_strategy")
            if preferred_strategy and preferred_strategy != base_strategy.service_type.value:
                optimized_strategy.service_type = ServiceType(preferred_strategy)
                optimized_strategy.reasoning += f" (用户偏好: {preferred_strategy})"
        
        return optimized_strategy

class StrategyScheduler:
    def __init__(self):
        self.strategy_rules = StrategyRules()
        self.performance_monitor = PerformanceMonitor()
        self.adaptive_selector = AdaptiveSelector()
    
    async def select_strategy(self, intent: IntentInfo) -> RetrievalStrategy:
        # 1. 基于规则的策略选择
        base_strategy = self.strategy_rules.get_strategy(intent)
        
        # 2. 性能监控调整
        performance_adjustment = self.performance_monitor.get_adjustment(intent)
        
        # 3. 自适应选择
        final_strategy = self.adaptive_selector.optimize(
            base_strategy, 
            performance_adjustment,
            intent
        )
        
        return final_strategy
    
    def get_strategy_by_name(self, strategy_name: str) -> RetrievalStrategy:
        strategy_map = {
            "vector": RetrievalStrategy(
                service_type=ServiceType.VECTOR,
                strategy_name="向量检索",
                parameters={"top_k": 10, "similarity_threshold": 0.7},
                reasoning="强制使用向量检索",
                confidence=1.0
            ),
            "hybrid": RetrievalStrategy(
                service_type=ServiceType.HYBRID,
                strategy_name="混合检索",
                parameters={"vector_weight": 0.7, "keyword_weight": 0.3, "top_k": 10},
                reasoning="强制使用混合检索",
                confidence=1.0
            ),
            "enhanced": RetrievalStrategy(
                service_type=ServiceType.ENHANCED,
                strategy_name="增强检索流水线",
                parameters={"enable_expansion": True, "enable_rerank": True, "top_k": 15},
                reasoning="强制使用增强检索流水线",
                confidence=1.0
            ),
            "keyword": RetrievalStrategy(
                service_type=ServiceType.KEYWORD,
                strategy_name="关键词检索",
                parameters={"top_k": 10},
                reasoning="强制使用关键词检索",
                confidence=1.0
            )
        }
        return strategy_map.get(strategy_name, strategy_map["vector"]) 