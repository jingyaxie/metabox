"""
HybridRetriever 混合检索模块
支持向量检索和关键词检索的融合
"""
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class FusionStrategy(str, Enum):
    """融合策略"""
    WEIGHTED_SUM = "weighted_sum"           # 加权求和
    RECIPROCAL_RANK = "reciprocal_rank"     # 倒数排名融合
    COMB_SUM = "comb_sum"                   # 组合求和
    COMB_MNZ = "comb_mnz"                   # 组合最大归一化
    BORDA_COUNT = "borda_count"             # Borda计数


class HybridRetriever:
    """混合检索器"""
    
    def __init__(self, vector_service, keyword_service=None, 
                 weights: Optional[Dict[str, float]] = None,
                 fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_SUM):
        self.vector_service = vector_service
        self.keyword_service = keyword_service
        self.weights = weights or {"vector": 0.7, "keyword": 0.3}
        self.fusion_strategy = fusion_strategy
        
        # 确保权重和为1
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            self.weights = {k: v / total_weight for k, v in self.weights.items()}
    
    async def retrieve(self, query: str, kb_ids: List[str], top_k: int = 10) -> List[Dict]:
        """混合检索主入口"""
        try:
            # 1. 并行执行向量检索和关键词检索
            search_tasks = []
            
            # 向量检索
            if self.vector_service:
                search_tasks.append(
                    self._vector_search(query, kb_ids, top_k * 2)
                )
            
            # 关键词检索
            if self.keyword_service:
                search_tasks.append(
                    self._keyword_search(query, kb_ids, top_k * 2)
                )
            
            # 如果没有可用的检索服务，降级到简单检索
            if not search_tasks:
                logger.warning("没有可用的检索服务，使用降级检索")
                return await self._fallback_search(query, kb_ids, top_k)
            
            # 并行执行检索
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # 2. 处理检索结果
            vector_results = []
            keyword_results = []
            
            for i, result in enumerate(search_results):
                if isinstance(result, Exception):
                    logger.error(f"检索失败 {i}: {result}")
                    continue
                
                if i == 0 and self.vector_service:
                    vector_results = result
                elif i == 1 and self.keyword_service:
                    keyword_results = result
            
            # 3. 结果融合
            if vector_results and keyword_results:
                merged_results = self._merge_results(vector_results, keyword_results)
            elif vector_results:
                merged_results = vector_results
            elif keyword_results:
                merged_results = keyword_results
            else:
                logger.warning("所有检索都失败，返回空结果")
                return []
            
            # 4. 去重和排序
            final_results = self._deduplicate_and_sort(merged_results, top_k)
            
            return final_results
            
        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            return await self._fallback_search(query, kb_ids, top_k)
    
    async def _vector_search(self, query: str, kb_ids: List[str], top_k: int) -> List[Dict]:
        """向量检索"""
        try:
            # 使用现有的向量服务
            search_results = await self.vector_service.hybrid_search(query, kb_ids, top_k)
            
            # 处理结果格式
            vector_results = []
            if "text" in search_results:
                for result in search_results["text"]:
                    vector_results.append({
                        "id": result["id"],
                        "content": result["content"],
                        "score": result["score"],
                        "source": "vector",
                        "source_file": result.get("source_file", ""),
                        "knowledge_base_id": result.get("knowledge_base_id", ""),
                        "metadata": result.get("metadata", {})
                    })
            
            return vector_results
            
        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []
    
    async def _keyword_search(self, query: str, kb_ids: List[str], top_k: int) -> List[Dict]:
        """关键词检索"""
        try:
            if not self.keyword_service:
                return []
            
            # 使用关键词服务进行检索
            keyword_results = await self.keyword_service.search(query, kb_ids, top_k)
            
            # 处理结果格式
            processed_results = []
            for result in keyword_results:
                processed_results.append({
                    "id": result["id"],
                    "content": result["content"],
                    "score": result["score"],
                    "source": "keyword",
                    "source_file": result.get("source_file", ""),
                    "knowledge_base_id": result.get("knowledge_base_id", ""),
                    "metadata": result.get("metadata", {})
                })
            
            return processed_results
            
        except Exception as e:
            logger.error(f"关键词检索失败: {e}")
            return []
    
    def _merge_results(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """融合检索结果"""
        if self.fusion_strategy == FusionStrategy.WEIGHTED_SUM:
            return self._weighted_sum_fusion(vector_results, keyword_results)
        elif self.fusion_strategy == FusionStrategy.RECIPROCAL_RANK:
            return self._reciprocal_rank_fusion(vector_results, keyword_results)
        elif self.fusion_strategy == FusionStrategy.COMB_SUM:
            return self._comb_sum_fusion(vector_results, keyword_results)
        elif self.fusion_strategy == FusionStrategy.COMB_MNZ:
            return self._comb_mnz_fusion(vector_results, keyword_results)
        elif self.fusion_strategy == FusionStrategy.BORDA_COUNT:
            return self._borda_count_fusion(vector_results, keyword_results)
        else:
            return self._weighted_sum_fusion(vector_results, keyword_results)
    
    def _weighted_sum_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """加权求和融合"""
        # 创建文档ID到结果的映射
        doc_scores = defaultdict(lambda: {"vector_score": 0.0, "keyword_score": 0.0, "doc": None})
        
        # 处理向量检索结果
        for i, result in enumerate(vector_results):
            doc_id = result["id"]
            doc_scores[doc_id]["vector_score"] = result["score"]
            doc_scores[doc_id]["doc"] = result
        
        # 处理关键词检索结果
        for i, result in enumerate(keyword_results):
            doc_id = result["id"]
            doc_scores[doc_id]["keyword_score"] = result["score"]
            if doc_scores[doc_id]["doc"] is None:
                doc_scores[doc_id]["doc"] = result
        
        # 计算融合分数
        merged_results = []
        for doc_id, scores in doc_scores.items():
            doc = scores["doc"]
            fused_score = (
                scores["vector_score"] * self.weights["vector"] +
                scores["keyword_score"] * self.weights["keyword"]
            )
            
            merged_results.append({
                **doc,
                "fused_score": fused_score,
                "vector_score": scores["vector_score"],
                "keyword_score": scores["keyword_score"]
            })
        
        return merged_results
    
    def _reciprocal_rank_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """倒数排名融合"""
        doc_ranks = defaultdict(lambda: {"vector_rank": float('inf'), "keyword_rank": float('inf'), "doc": None})
        
        # 记录向量检索排名
        for i, result in enumerate(vector_results):
            doc_id = result["id"]
            doc_ranks[doc_id]["vector_rank"] = i + 1
            doc_ranks[doc_id]["doc"] = result
        
        # 记录关键词检索排名
        for i, result in enumerate(keyword_results):
            doc_id = result["id"]
            doc_ranks[doc_id]["keyword_rank"] = i + 1
            if doc_ranks[doc_id]["doc"] is None:
                doc_ranks[doc_id]["doc"] = result
        
        # 计算融合分数
        merged_results = []
        for doc_id, ranks in doc_ranks.items():
            doc = ranks["doc"]
            fused_score = (
                1.0 / ranks["vector_rank"] * self.weights["vector"] +
                1.0 / ranks["keyword_rank"] * self.weights["keyword"]
            )
            
            merged_results.append({
                **doc,
                "fused_score": fused_score,
                "vector_rank": ranks["vector_rank"],
                "keyword_rank": ranks["keyword_rank"]
            })
        
        return merged_results
    
    def _comb_sum_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """组合求和融合"""
        return self._weighted_sum_fusion(vector_results, keyword_results)
    
    def _comb_mnz_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """组合最大归一化融合"""
        # 获取最大分数用于归一化
        max_vector_score = max([r["score"] for r in vector_results]) if vector_results else 1.0
        max_keyword_score = max([r["score"] for r in keyword_results]) if keyword_results else 1.0
        
        doc_scores = defaultdict(lambda: {"vector_score": 0.0, "keyword_score": 0.0, "doc": None})
        
        # 处理向量检索结果
        for result in vector_results:
            doc_id = result["id"]
            doc_scores[doc_id]["vector_score"] = result["score"] / max_vector_score
            doc_scores[doc_id]["doc"] = result
        
        # 处理关键词检索结果
        for result in keyword_results:
            doc_id = result["id"]
            doc_scores[doc_id]["keyword_score"] = result["score"] / max_keyword_score
            if doc_scores[doc_id]["doc"] is None:
                doc_scores[doc_id]["doc"] = result
        
        # 计算融合分数
        merged_results = []
        for doc_id, scores in doc_scores.items():
            doc = scores["doc"]
            fused_score = (
                scores["vector_score"] * self.weights["vector"] +
                scores["keyword_score"] * self.weights["keyword"]
            )
            
            merged_results.append({
                **doc,
                "fused_score": fused_score,
                "vector_score": scores["vector_score"],
                "keyword_score": scores["keyword_score"]
            })
        
        return merged_results
    
    def _borda_count_fusion(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """Borda计数融合"""
        doc_scores = defaultdict(lambda: {"vector_score": 0.0, "keyword_score": 0.0, "doc": None})
        
        # 计算Borda分数
        max_rank = max(len(vector_results), len(keyword_results))
        
        # 处理向量检索结果
        for i, result in enumerate(vector_results):
            doc_id = result["id"]
            doc_scores[doc_id]["vector_score"] = max_rank - i
            doc_scores[doc_id]["doc"] = result
        
        # 处理关键词检索结果
        for i, result in enumerate(keyword_results):
            doc_id = result["id"]
            doc_scores[doc_id]["keyword_score"] = max_rank - i
            if doc_scores[doc_id]["doc"] is None:
                doc_scores[doc_id]["doc"] = result
        
        # 计算融合分数
        merged_results = []
        for doc_id, scores in doc_scores.items():
            doc = scores["doc"]
            fused_score = (
                scores["vector_score"] * self.weights["vector"] +
                scores["keyword_score"] * self.weights["keyword"]
            )
            
            merged_results.append({
                **doc,
                "fused_score": fused_score,
                "vector_score": scores["vector_score"],
                "keyword_score": scores["keyword_score"]
            })
        
        return merged_results
    
    def _deduplicate_and_sort(self, results: List[Dict], top_k: int) -> List[Dict]:
        """去重和排序"""
        # 按文档ID去重，保留最高分数的版本
        unique_docs = {}
        for result in results:
            doc_id = result["id"]
            if doc_id not in unique_docs or result.get("fused_score", result["score"]) > unique_docs[doc_id].get("fused_score", unique_docs[doc_id]["score"]):
                unique_docs[doc_id] = result
        
        # 按融合分数排序
        sorted_results = sorted(
            unique_docs.values(),
            key=lambda x: x.get("fused_score", x["score"]),
            reverse=True
        )
        
        return sorted_results[:top_k]
    
    async def _fallback_search(self, query: str, kb_ids: List[str], top_k: int) -> List[Dict]:
        """降级检索"""
        logger.warning("使用降级检索")
        
        # 简单的关键词匹配
        if not self.vector_service:
            return []
        
        try:
            # 尝试使用向量服务的简单搜索
            search_results = await self.vector_service.search_text(query, kb_ids, top_k)
            
            return [
                {
                    "id": result["id"],
                    "content": result["content"],
                    "score": result["score"],
                    "source": "fallback",
                    "source_file": result.get("source_file", ""),
                    "knowledge_base_id": result.get("knowledge_base_id", ""),
                    "metadata": result.get("metadata", {})
                }
                for result in search_results
            ]
        except Exception as e:
            logger.error(f"降级检索也失败: {e}")
            return []
    
    def get_retrieval_stats(self, query: str, results: List[Dict]) -> Dict[str, Any]:
        """获取检索统计信息"""
        vector_count = len([r for r in results if r.get("source") == "vector"])
        keyword_count = len([r for r in results if r.get("source") == "keyword"])
        fallback_count = len([r for r in results if r.get("source") == "fallback"])
        
        return {
            "total_results": len(results),
            "vector_results": vector_count,
            "keyword_results": keyword_count,
            "fallback_results": fallback_count,
            "fusion_strategy": self.fusion_strategy.value,
            "weights": self.weights
        } 