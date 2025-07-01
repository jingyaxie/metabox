"""
意图识别器
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio

class QueryType(str, Enum):
    FACTUAL = "factual"
    CONCEPTUAL = "conceptual"
    PROCEDURAL = "procedural"
    COMPARATIVE = "comparative"
    TROUBLESHOOTING = "troubleshooting"
    UNKNOWN = "unknown"

class Complexity(str, Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"
    MULTI_TURN = "multi_turn"

@dataclass
class IntentInfo:
    query_type: QueryType
    complexity: Complexity
    confidence: float
    features: Dict[str, Any]
    user_profile: Optional[Dict[str, Any]] = None
    context_info: Optional[Dict[str, Any]] = None

class QueryClassifier:
    def __init__(self):
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
    async def classify(self, query: str) -> QueryType:
        query_lower = query.lower()
        type_scores = {}
        for query_type, keywords in self.type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            type_scores[query_type] = score
        if type_scores:
            best_type = max(type_scores.items(), key=lambda x: x[1])
            if best_type[1] > 0:
                return best_type[0]
        return QueryType.UNKNOWN

class ComplexityAnalyzer:
    def __init__(self):
        self.complexity_features = {
            "length_threshold": 50,
            "concept_count_threshold": 3,
            "question_mark_weight": 2,
            "and_or_weight": 1.5,
        }
    async def analyze(self, query: str) -> Complexity:
        score = 0
        if len(query) > self.complexity_features["length_threshold"]:
            score += 2
        concept_count = len(query.split())
        if concept_count > self.complexity_features["concept_count_threshold"]:
            score += 1
        question_count = query.count("?") + query.count("？")
        score += question_count * self.complexity_features["question_mark_weight"]
        connectors = ["和", "或", "与", "and", "or", "with"]
        connector_count = sum(1 for conn in connectors if conn in query.lower())
        score += connector_count * self.complexity_features["and_or_weight"]
        if score >= 3:
            return Complexity.COMPLEX
        elif score >= 1:
            return Complexity.SIMPLE
        else:
            return Complexity.SIMPLE

class UserProfiler:
    def __init__(self):
        self.user_profiles = {}
    async def get_profile(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        user_id = user_context.get("user_id")
        if not user_id:
            return self._get_default_profile()
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        profile = self._get_default_profile()
        self.user_profiles[user_id] = profile
        return profile
    def _get_default_profile(self) -> Dict[str, Any]:
        return {
            "preferred_strategy": "hybrid",
            "complexity_level": "simple",
            "response_speed": "normal",
            "technical_level": "intermediate"
        }

class ContextAnalyzer:
    def __init__(self):
        pass
    async def analyze(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        context_info = {
            "has_conversation_history": False,
            "conversation_length": 0,
            "recent_topics": [],
            "session_duration": 0
        }
        conversation_history = user_context.get("conversation_history", [])
        if conversation_history:
            context_info["has_conversation_history"] = True
            context_info["conversation_length"] = len(conversation_history)
            recent_queries = [item["query"] for item in conversation_history[-3:]]
            context_info["recent_topics"] = recent_queries
        return context_info

class IntentRecognizer:
    def __init__(self):
        self.query_classifier = QueryClassifier()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.user_profiler = UserProfiler()
        self.context_analyzer = ContextAnalyzer()
    async def recognize_intent(self, query: str, user_context: Dict) -> IntentInfo:
        query_type, complexity, user_profile, context_info = await asyncio.gather(
            self.query_classifier.classify(query),
            self.complexity_analyzer.analyze(query),
            self.user_profiler.get_profile(user_context),
            self.context_analyzer.analyze(user_context)
        )
        confidence = 0.5
        if query_type != QueryType.UNKNOWN:
            confidence += 0.3
        if complexity == Complexity.SIMPLE:
            confidence += 0.1
        elif complexity == Complexity.COMPLEX:
            confidence += 0.2
        if context_info.get("has_conversation_history"):
            confidence += 0.1
        confidence = min(1.0, confidence)
        features = {
            "query_length": len(query),
            "word_count": len(query.split()),
            "has_question_mark": "?" in query or "？" in query,
            "has_connectors": any(conn in query.lower() for conn in ["和", "或", "与", "and", "or"]),
            "query_type": query_type.value,
            "complexity": complexity.value
        }
        return IntentInfo(
            query_type=query_type,
            complexity=complexity,
            confidence=confidence,
            features=features,
            user_profile=user_profile,
            context_info=context_info
        ) 