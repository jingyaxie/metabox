"""
高级预览服务
支持分块预览、性能预估和配置优化建议
"""
from typing import List, Dict, Any, Optional, Tuple
import time
import asyncio
from dataclasses import dataclass
import logging

from app.services.hybrid_chunker import HybridChunker, HybridChunk
from app.services.embedding_router import EmbeddingRouter, EmbeddingModel

logger = logging.getLogger(__name__)


@dataclass
class PreviewChunk:
    """预览分块"""
    chunk_id: str
    content: str
    chunk_type: str
    size: int
    token_estimate: int
    parent_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class PerformanceEstimate:
    """性能预估"""
    total_chunks: int
    total_tokens: int
    embedding_cost: float
    processing_time_estimate: float
    storage_size_estimate: int
    retrieval_speed_estimate: float


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    suggestion_type: str
    description: str
    impact: str  # high, medium, low
    current_value: Any
    suggested_value: Any
    reasoning: str


class AdvancedPreviewService:
    """高级预览服务"""
    
    def __init__(self):
        self.hybrid_chunker = HybridChunker()
        self.embedding_router = EmbeddingRouter()
    
    async def get_comprehensive_preview(
        self,
        content: str,
        config: Dict[str, Any],
        preview_type: str = "full"
    ) -> Dict[str, Any]:
        """获取综合预览"""
        start_time = time.time()
        
        # 解析配置
        chunk_size = config.get("chunk_size", 512)
        chunk_overlap = config.get("chunk_overlap", 50)
        embedding_model = config.get("embedding_model", "bge-m3")
        use_hybrid = config.get("use_hybrid", True)
        use_markdown = config.get("use_markdown", True)
        
        # 创建分块预览
        preview_chunks = await self._create_preview_chunks(
            content, chunk_size, chunk_overlap, use_hybrid, use_markdown
        )
        
        # 性能预估
        performance = await self._estimate_performance(
            preview_chunks, embedding_model
        )
        
        # 配置优化建议
        suggestions = await self._generate_optimization_suggestions(
            content, preview_chunks, config
        )
        
        # 分块层次结构
        hierarchy = self._get_preview_hierarchy(preview_chunks)
        
        # 统计信息
        statistics = self._get_preview_statistics(preview_chunks)
        
        preview_time = time.time() - start_time
        
        return {
            "preview_type": preview_type,
            "preview_time": preview_time,
            "chunks": [self._chunk_to_dict(chunk) for chunk in preview_chunks],
            "performance": self._performance_to_dict(performance),
            "suggestions": [self._suggestion_to_dict(s) for s in suggestions],
            "hierarchy": hierarchy,
            "statistics": statistics,
            "config_used": config
        }
    
    async def _create_preview_chunks(
        self,
        content: str,
        chunk_size: int,
        chunk_overlap: int,
        use_hybrid: bool,
        use_markdown: bool
    ) -> List[PreviewChunk]:
        """创建预览分块"""
        preview_chunks = []
        
        if use_hybrid:
            # 使用混合分块
            hybrid_chunks = await self.hybrid_chunker.create_hybrid_chunks(
                content,
                parent_chunk_size=chunk_size * 2,
                child_chunk_size=chunk_size,
                child_overlap=chunk_overlap,
                use_markdown_structure=use_markdown
            )
            
            for chunk in hybrid_chunks:
                preview_chunk = PreviewChunk(
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type.value,
                    size=len(chunk.content),
                    token_estimate=self._estimate_tokens(chunk.content),
                    parent_id=chunk.parent_id,
                    metadata=chunk.metadata
                )
                preview_chunks.append(preview_chunk)
        else:
            # 使用简单分块
            simple_chunks = await self.hybrid_chunker.create_semantic_chunks(
                content, chunk_size
            )
            
            for chunk in simple_chunks:
                preview_chunk = PreviewChunk(
                    chunk_id=chunk.chunk_id,
                    content=chunk.content,
                    chunk_type="standalone",
                    size=len(chunk.content),
                    token_estimate=self._estimate_tokens(chunk.content),
                    metadata=chunk.metadata
                )
                preview_chunks.append(preview_chunk)
        
        return preview_chunks
    
    def _estimate_tokens(self, text: str) -> int:
        """估算token数量"""
        # 简单估算：英文约4字符1token，中文约2字符1token
        english_chars = sum(1 for c in text if c.isascii())
        chinese_chars = len(text) - english_chars
        
        return int(english_chars / 4 + chinese_chars / 2)
    
    async def _estimate_performance(
        self,
        chunks: List[PreviewChunk],
        embedding_model: str
    ) -> PerformanceEstimate:
        """预估性能"""
        total_chunks = len(chunks)
        total_tokens = sum(chunk.token_estimate for chunk in chunks)
        
        # 估算embedding成本
        model = EmbeddingModel(embedding_model)
        embedding_cost = self.embedding_router.estimate_cost(
            " ".join(chunk.content for chunk in chunks), model
        )
        
        # 估算处理时间
        processing_time = total_chunks * 0.1  # 假设每个分块0.1秒
        
        # 估算存储大小
        storage_size = total_chunks * 1024  # 假设每个向量1KB
        
        # 估算检索速度
        retrieval_speed = 1000 / total_chunks if total_chunks > 0 else 0
        
        return PerformanceEstimate(
            total_chunks=total_chunks,
            total_tokens=total_tokens,
            embedding_cost=embedding_cost,
            processing_time_estimate=processing_time,
            storage_size_estimate=storage_size,
            retrieval_speed_estimate=retrieval_speed
        )
    
    async def _generate_optimization_suggestions(
        self,
        content: str,
        chunks: List[PreviewChunk],
        config: Dict[str, Any]
    ) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        suggestions = []
        
        # 分析分块大小
        chunk_sizes = [chunk.size for chunk in chunks]
        avg_size = sum(chunk_sizes) / len(chunk_sizes) if chunk_sizes else 0
        
        if avg_size > 800:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="chunk_size",
                description="分块大小过大，建议减小",
                impact="high",
                current_value=config.get("chunk_size", 512),
                suggested_value=max(256, config.get("chunk_size", 512) - 128),
                reasoning="当前平均分块大小过大，可能影响检索精度"
            ))
        elif avg_size < 200:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="chunk_size",
                description="分块大小过小，建议增大",
                impact="medium",
                current_value=config.get("chunk_size", 512),
                suggested_value=min(1024, config.get("chunk_size", 512) + 128),
                reasoning="当前平均分块大小过小，可能丢失上下文信息"
            ))
        
        # 分析重叠度
        overlap = config.get("chunk_overlap", 50)
        if overlap < 20:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="chunk_overlap",
                description="重叠度过低，建议增加",
                impact="medium",
                current_value=overlap,
                suggested_value=min(100, overlap + 30),
                reasoning="重叠度过低可能导致信息丢失"
            ))
        elif overlap > 200:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="chunk_overlap",
                description="重叠度过高，建议减少",
                impact="low",
                current_value=overlap,
                suggested_value=max(50, overlap - 50),
                reasoning="重叠度过高会增加存储和处理成本"
            ))
        
        # 分析embedding模型
        current_model = config.get("embedding_model", "bge-m3")
        content_length = len(content)
        
        if content_length > 10000 and current_model in ["text-embedding-ada-002", "text-embedding-3-small"]:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="embedding_model",
                description="长文档建议使用本地模型",
                impact="high",
                current_value=current_model,
                suggested_value="bge-m3",
                reasoning="长文档使用本地模型可以降低成本"
            ))
        elif content_length < 1000 and current_model in ["bge-m3", "gte-large"]:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="embedding_model",
                description="短文档建议使用OpenAI模型",
                impact="medium",
                current_value=current_model,
                suggested_value="text-embedding-3-small",
                reasoning="短文档使用OpenAI模型可以获得更好的语义理解"
            ))
        
        # 分析混合分块
        if not config.get("use_hybrid", True) and len(content) > 5000:
            suggestions.append(OptimizationSuggestion(
                suggestion_type="use_hybrid",
                description="长文档建议启用混合分块",
                impact="high",
                current_value=False,
                suggested_value=True,
                reasoning="混合分块可以更好地保持文档结构"
            ))
        
        return suggestions
    
    def _get_preview_hierarchy(self, chunks: List[PreviewChunk]) -> Dict[str, Any]:
        """获取预览层次结构"""
        hierarchy = {
            "parents": [],
            "children": [],
            "standalone": []
        }
        
        for chunk in chunks:
            chunk_info = {
                "id": chunk.chunk_id,
                "content_preview": chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content,
                "size": chunk.size,
                "token_estimate": chunk.token_estimate,
                "metadata": chunk.metadata
            }
            
            if chunk.chunk_type == "parent":
                hierarchy["parents"].append(chunk_info)
            elif chunk.chunk_type == "child":
                chunk_info["parent_id"] = chunk.parent_id
                hierarchy["children"].append(chunk_info)
            else:
                hierarchy["standalone"].append(chunk_info)
        
        return hierarchy
    
    def _get_preview_statistics(self, chunks: List[PreviewChunk]) -> Dict[str, Any]:
        """获取预览统计信息"""
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_size": 0,
                "total_tokens": 0,
                "size_distribution": {}
            }
        
        sizes = [chunk.size for chunk in chunks]
        tokens = [chunk.token_estimate for chunk in chunks]
        
        # 大小分布
        size_ranges = {
            "small": len([s for s in sizes if s < 200]),
            "medium": len([s for s in sizes if 200 <= s < 500]),
            "large": len([s for s in sizes if s >= 500])
        }
        
        return {
            "total_chunks": len(chunks),
            "avg_size": sum(sizes) / len(sizes),
            "min_size": min(sizes),
            "max_size": max(sizes),
            "total_tokens": sum(tokens),
            "avg_tokens": sum(tokens) / len(tokens),
            "size_distribution": size_ranges
        }
    
    def _chunk_to_dict(self, chunk: PreviewChunk) -> Dict[str, Any]:
        """转换分块为字典"""
        return {
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "chunk_type": chunk.chunk_type,
            "size": chunk.size,
            "token_estimate": chunk.token_estimate,
            "parent_id": chunk.parent_id,
            "metadata": chunk.metadata
        }
    
    def _performance_to_dict(self, performance: PerformanceEstimate) -> Dict[str, Any]:
        """转换性能预估为字典"""
        return {
            "total_chunks": performance.total_chunks,
            "total_tokens": performance.total_tokens,
            "embedding_cost": performance.embedding_cost,
            "processing_time_estimate": performance.processing_time_estimate,
            "storage_size_estimate": performance.storage_size_estimate,
            "retrieval_speed_estimate": performance.retrieval_speed_estimate
        }
    
    def _suggestion_to_dict(self, suggestion: OptimizationSuggestion) -> Dict[str, Any]:
        """转换优化建议为字典"""
        return {
            "suggestion_type": suggestion.suggestion_type,
            "description": suggestion.description,
            "impact": suggestion.impact,
            "current_value": suggestion.current_value,
            "suggested_value": suggestion.suggested_value,
            "reasoning": suggestion.reasoning
        }
    
    async def get_quick_preview(self, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取快速预览"""
        # 只预览前1000字符
        preview_content = content[:1000]
        if len(content) > 1000:
            preview_content += "\n\n[内容已截断，仅显示前1000字符]"
        
        return await self.get_comprehensive_preview(preview_content, config, "quick")
    
    async def get_batch_preview(self, contents: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """批量预览"""
        previews = []
        
        for i, content in enumerate(contents):
            try:
                preview = await self.get_comprehensive_preview(content, config, "batch")
                preview["content_index"] = i
                previews.append(preview)
            except Exception as e:
                logger.error(f"批量预览失败 {i}: {e}")
                previews.append({
                    "content_index": i,
                    "error": str(e),
                    "preview_type": "batch"
                })
        
        return previews
    
    async def compare_configs(
        self,
        content: str,
        configs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """比较不同配置的效果"""
        comparisons = []
        
        for i, config in enumerate(configs):
            try:
                preview = await self.get_comprehensive_preview(content, config, "comparison")
                comparisons.append({
                    "config_index": i,
                    "config": config,
                    "performance": preview["performance"],
                    "statistics": preview["statistics"],
                    "suggestions": preview["suggestions"]
                })
            except Exception as e:
                logger.error(f"配置比较失败 {i}: {e}")
                comparisons.append({
                    "config_index": i,
                    "config": config,
                    "error": str(e)
                })
        
        # 生成比较报告
        comparison_report = self._generate_comparison_report(comparisons)
        
        return {
            "comparisons": comparisons,
            "report": comparison_report
        }
    
    def _generate_comparison_report(self, comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成比较报告"""
        valid_comparisons = [c for c in comparisons if "error" not in c]
        
        if not valid_comparisons:
            return {"error": "没有有效的配置比较"}
        
        # 找出最佳配置
        best_performance = min(valid_comparisons, key=lambda x: x["performance"]["embedding_cost"])
        best_quality = max(valid_comparisons, key=lambda x: x["statistics"]["avg_size"])
        
        return {
            "best_cost_config": best_performance["config_index"],
            "best_quality_config": best_quality["config_index"],
            "total_configs": len(comparisons),
            "valid_configs": len(valid_comparisons)
        } 