"""
Reranker 重排序模块
支持cross-encoder重排序和规则重排序
"""
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
import re
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RerankStrategy(str, Enum):
    """重排序策略"""
    CROSS_ENCODER = "cross_encoder"     # Cross-encoder模型重排序
    RULE_BASED = "rule_based"           # 规则重排序
    HYBRID = "hybrid"                   # 混合重排序


@dataclass
class RerankResult:
    """重排序结果"""
    id: str
    content: str
    original_score: float
    rerank_score: float
    final_score: float
    source_file: str
    knowledge_base_id: str
    metadata: Dict[str, Any]
    rerank_reason: str = ""


class Reranker:
    """重排序器"""
    
    def __init__(self, cross_encoder_client=None, strategy: RerankStrategy = RerankStrategy.HYBRID):
        self.cross_encoder_client = cross_encoder_client
        self.strategy = strategy
        
        # 规则重排序权重
        self.rule_weights = {
            "exact_match": 0.3,      # 精确匹配
            "keyword_density": 0.2,   # 关键词密度
            "length_penalty": 0.1,    # 长度惩罚
            "freshness": 0.1,         # 新鲜度
            "source_quality": 0.1,    # 来源质量
            "position_bonus": 0.1,    # 位置奖励
            "format_quality": 0.1     # 格式质量
        }
    
    async def rerank(self, query: str, documents: List[Dict], top_k: int = 10) -> List[RerankResult]:
        """重排序主入口"""
        try:
            if not documents:
                return []
            
            # 根据策略选择重排序方法
            if self.strategy == RerankStrategy.CROSS_ENCODER:
                return await self._cross_encoder_rerank(query, documents, top_k)
            elif self.strategy == RerankStrategy.RULE_BASED:
                return self._rule_based_rerank(query, documents, top_k)
            else:  # HYBRID
                return await self._hybrid_rerank(query, documents, top_k)
                
        except Exception as e:
            logger.error(f"重排序失败: {e}")
            # 降级到原始排序
            return self._fallback_rerank(documents, top_k)
    
    async def _cross_encoder_rerank(self, query: str, documents: List[Dict], top_k: int) -> List[RerankResult]:
        """Cross-encoder重排序"""
        if not self.cross_encoder_client:
            logger.warning("Cross-encoder客户端不可用，使用规则重排序")
            return self._rule_based_rerank(query, documents, top_k)
        
        try:
            # 准备查询-文档对
            query_doc_pairs = []
            for doc in documents:
                query_doc_pairs.append((query, doc["content"]))
            
            # 批量计算相关性分数
            scores = await self.cross_encoder_client.predict(query_doc_pairs)
            
            # 构建重排序结果
            rerank_results = []
            for i, doc in enumerate(documents):
                rerank_score = scores[i] if i < len(scores) else 0.0
                original_score = doc.get("score", 0.0)
                
                # 计算最终分数（结合原始分数和重排序分数）
                final_score = self._combine_scores(original_score, rerank_score)
                
                rerank_results.append(RerankResult(
                    id=doc["id"],
                    content=doc["content"],
                    original_score=original_score,
                    rerank_score=rerank_score,
                    final_score=final_score,
                    source_file=doc.get("source_file", ""),
                    knowledge_base_id=doc.get("knowledge_base_id", ""),
                    metadata=doc.get("metadata", {}),
                    rerank_reason="cross_encoder"
                ))
            
            # 按最终分数排序
            rerank_results.sort(key=lambda x: x.final_score, reverse=True)
            return rerank_results[:top_k]
            
        except Exception as e:
            logger.error(f"Cross-encoder重排序失败: {e}")
            return self._rule_based_rerank(query, documents, top_k)
    
    def _rule_based_rerank(self, query: str, documents: List[Dict], top_k: int) -> List[RerankResult]:
        """规则重排序"""
        rerank_results = []
        
        for doc in documents:
            # 计算各项规则分数
            exact_match_score = self._calculate_exact_match(query, doc["content"])
            keyword_density_score = self._calculate_keyword_density(query, doc["content"])
            length_penalty_score = self._calculate_length_penalty(doc["content"])
            freshness_score = self._calculate_freshness(doc.get("metadata", {}))
            source_quality_score = self._calculate_source_quality(doc.get("metadata", {}))
            position_bonus_score = self._calculate_position_bonus(doc.get("metadata", {}))
            format_quality_score = self._calculate_format_quality(doc["content"])
            
            # 计算规则重排序分数
            rule_score = (
                exact_match_score * self.rule_weights["exact_match"] +
                keyword_density_score * self.rule_weights["keyword_density"] +
                length_penalty_score * self.rule_weights["length_penalty"] +
                freshness_score * self.rule_weights["freshness"] +
                source_quality_score * self.rule_weights["source_quality"] +
                position_bonus_score * self.rule_weights["position_bonus"] +
                format_quality_score * self.rule_weights["format_quality"]
            )
            
            original_score = doc.get("score", 0.0)
            final_score = self._combine_scores(original_score, rule_score)
            
            rerank_results.append(RerankResult(
                id=doc["id"],
                content=doc["content"],
                original_score=original_score,
                rerank_score=rule_score,
                final_score=final_score,
                source_file=doc.get("source_file", ""),
                knowledge_base_id=doc.get("knowledge_base_id", ""),
                metadata=doc.get("metadata", {}),
                rerank_reason="rule_based"
            ))
        
        # 按最终分数排序
        rerank_results.sort(key=lambda x: x.final_score, reverse=True)
        return rerank_results[:top_k]
    
    async def _hybrid_rerank(self, query: str, documents: List[Dict], top_k: int) -> List[RerankResult]:
        """混合重排序"""
        # 先进行规则重排序
        rule_results = self._rule_based_rerank(query, documents, top_k * 2)
        
        # 对前N个结果进行Cross-encoder重排序
        if self.cross_encoder_client and rule_results:
            try:
                # 准备查询-文档对
                query_doc_pairs = []
                for result in rule_results[:top_k]:
                    query_doc_pairs.append((query, result.content))
                
                # 批量计算相关性分数
                scores = await self.cross_encoder_client.predict(query_doc_pairs)
                
                # 更新重排序分数
                for i, result in enumerate(rule_results[:top_k]):
                    if i < len(scores):
                        cross_encoder_score = scores[i]
                        # 结合规则分数和Cross-encoder分数
                        result.rerank_score = (result.rerank_score + cross_encoder_score) / 2
                        result.final_score = self._combine_scores(result.original_score, result.rerank_score)
                        result.rerank_reason = "hybrid"
                
            except Exception as e:
                logger.error(f"混合重排序中Cross-encoder失败: {e}")
        
        return rule_results[:top_k]
    
    def _calculate_exact_match(self, query: str, content: str) -> float:
        """计算精确匹配分数"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        # 计算查询词在内容中的匹配度
        matched_words = query_words.intersection(content_words)
        exact_match_ratio = len(matched_words) / len(query_words)
        
        # 检查连续短语匹配
        phrase_bonus = 0.0
        for i in range(len(query_words)):
            for j in range(i + 1, len(query_words) + 1):
                phrase = " ".join(list(query_words)[i:j])
                if phrase in content.lower():
                    phrase_bonus += 0.1
        
        return min(1.0, exact_match_ratio + phrase_bonus)
    
    def _calculate_keyword_density(self, query: str, content: str) -> float:
        """计算关键词密度分数"""
        query_words = query.lower().split()
        content_words = content.lower().split()
        
        if not content_words:
            return 0.0
        
        # 计算关键词在内容中的出现次数
        keyword_count = 0
        for word in query_words:
            keyword_count += content_words.count(word)
        
        # 计算密度
        density = keyword_count / len(content_words)
        
        # 归一化到0-1范围
        return min(1.0, density * 10)  # 假设密度0.1为满分
    
    def _calculate_length_penalty(self, content: str) -> float:
        """计算长度惩罚分数"""
        content_length = len(content)
        
        # 理想长度范围：100-1000字符
        if 100 <= content_length <= 1000:
            return 1.0
        elif content_length < 50:
            return 0.3  # 太短
        elif content_length > 2000:
            return 0.7  # 太长
        else:
            # 线性插值
            if content_length < 100:
                return 0.3 + (content_length - 50) / 50 * 0.7
            else:
                return 1.0 - (content_length - 1000) / 1000 * 0.3
    
    def _calculate_freshness(self, metadata: Dict[str, Any]) -> float:
        """计算新鲜度分数"""
        # 从元数据中提取时间信息
        created_at = metadata.get("created_at")
        updated_at = metadata.get("updated_at")
        
        if not created_at and not updated_at:
            return 0.5  # 默认中等分数
        
        # 这里可以添加时间计算逻辑
        # 暂时返回默认分数
        return 0.8
    
    def _calculate_source_quality(self, metadata: Dict[str, Any]) -> float:
        """计算来源质量分数"""
        source_type = metadata.get("source_type", "")
        source_quality = metadata.get("source_quality", 0.5)
        
        # 根据来源类型调整质量分数
        quality_weights = {
            "official_doc": 1.0,
            "tutorial": 0.9,
            "blog": 0.7,
            "forum": 0.5,
            "user_generated": 0.3
        }
        
        weight = quality_weights.get(source_type, 0.5)
        return source_quality * weight
    
    def _calculate_position_bonus(self, metadata: Dict[str, Any]) -> float:
        """计算位置奖励分数"""
        # 从元数据中提取位置信息
        position = metadata.get("position", 0)
        total_positions = metadata.get("total_positions", 1)
        
        if total_positions <= 1:
            return 1.0
        
        # 位置越靠前分数越高
        position_ratio = 1.0 - (position / total_positions)
        return position_ratio
    
    def _calculate_format_quality(self, content: str) -> float:
        """计算格式质量分数"""
        # 检查内容的格式质量
        score = 0.5  # 基础分数
        
        # 检查是否包含代码块
        if "```" in content or "<code>" in content:
            score += 0.2
        
        # 检查是否包含列表
        if re.search(r'^\s*[-*+]\s', content, re.MULTILINE) or re.search(r'^\s*\d+\.\s', content, re.MULTILINE):
            score += 0.1
        
        # 检查是否包含标题
        if re.search(r'^#{1,6}\s', content, re.MULTILINE):
            score += 0.1
        
        # 检查段落结构
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.1
        
        return min(1.0, score)
    
    def _combine_scores(self, original_score: float, rerank_score: float) -> float:
        """结合原始分数和重排序分数"""
        # 使用加权平均，原始分数权重0.3，重排序分数权重0.7
        return original_score * 0.3 + rerank_score * 0.7
    
    def _fallback_rerank(self, documents: List[Dict], top_k: int) -> List[RerankResult]:
        """降级重排序"""
        logger.warning("使用降级重排序")
        
        rerank_results = []
        for doc in documents:
            original_score = doc.get("score", 0.0)
            rerank_results.append(RerankResult(
                id=doc["id"],
                content=doc["content"],
                original_score=original_score,
                rerank_score=original_score,
                final_score=original_score,
                source_file=doc.get("source_file", ""),
                knowledge_base_id=doc.get("knowledge_base_id", ""),
                metadata=doc.get("metadata", {}),
                rerank_reason="fallback"
            ))
        
        # 按原始分数排序
        rerank_results.sort(key=lambda x: x.final_score, reverse=True)
        return rerank_results[:top_k]
    
    def get_rerank_stats(self, results: List[RerankResult]) -> Dict[str, Any]:
        """获取重排序统计信息"""
        if not results:
            return {}
        
        original_scores = [r.original_score for r in results]
        rerank_scores = [r.rerank_score for r in results]
        final_scores = [r.final_score for r in results]
        
        # 计算分数变化
        score_changes = [r.final_score - r.original_score for r in results]
        
        return {
            "total_results": len(results),
            "strategy": self.strategy.value,
            "avg_original_score": sum(original_scores) / len(original_scores),
            "avg_rerank_score": sum(rerank_scores) / len(rerank_scores),
            "avg_final_score": sum(final_scores) / len(final_scores),
            "avg_score_change": sum(score_changes) / len(score_changes),
            "max_score_change": max(score_changes),
            "min_score_change": min(score_changes),
            "rerank_reasons": list(set(r.rerank_reason for r in results))
        } 