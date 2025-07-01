"""
EnhancedRetrievalPipeline 增强检索流水线
整合查询预处理、多查询扩展、混合检索、重排序和元数据过滤
"""
from typing import List, Dict, Any, Optional, Tuple
import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum

from .query_processor import QueryProcessor
from .multi_query_expander import MultiQueryExpander, ExpansionStrategy, QueryType
from .hybrid_retriever import HybridRetriever, FusionStrategy
from .reranker import Reranker, RerankStrategy, RerankResult
from .metadata_filter import MetadataFilter, FilterCondition, FilterOperator

logger = logging.getLogger(__name__)


class PipelineStage(str, Enum):
    """流水线阶段"""
    QUERY_PREPROCESSING = "query_preprocessing"
    QUERY_EXPANSION = "query_expansion"
    METADATA_FILTERING = "metadata_filtering"
    HYBRID_RETRIEVAL = "hybrid_retrieval"
    RERANKING = "reranking"
    POST_PROCESSING = "post_processing"


@dataclass
class PipelineConfig:
    """流水线配置"""
    # 查询预处理配置
    enable_query_preprocessing: bool = True
    query_preprocessing_rules: List[str] = None
    
    # 查询扩展配置
    enable_query_expansion: bool = True
    expansion_strategy: ExpansionStrategy = ExpansionStrategy.HYBRID
    expansion_count: int = 3
    
    # 元数据过滤配置
    enable_metadata_filtering: bool = True
    predefined_filters: List[str] = None
    custom_conditions: List[FilterCondition] = None
    
    # 混合检索配置
    enable_hybrid_retrieval: bool = True
    fusion_strategy: FusionStrategy = FusionStrategy.WEIGHTED_SUM
    retrieval_weights: Dict[str, float] = None
    
    # 重排序配置
    enable_reranking: bool = True
    rerank_strategy: RerankStrategy = RerankStrategy.HYBRID
    rerank_top_k: int = 20
    
    # 通用配置
    max_retrieval_results: int = 50
    final_top_k: int = 10
    enable_parallel_processing: bool = True


@dataclass
class PipelineResult:
    """流水线结果"""
    query: str
    original_query: str
    expanded_queries: List[str]
    retrieved_documents: List[Dict]
    reranked_documents: List[RerankResult]
    final_documents: List[Dict]
    pipeline_stats: Dict[str, Any]
    stage_results: Dict[str, Any]
    processing_time: float


class EnhancedRetrievalPipeline:
    """增强检索流水线"""
    
    def __init__(self, 
                 vector_service=None,
                 keyword_service=None,
                 llm_client=None,
                 cross_encoder_client=None,
                 config: PipelineConfig = None):
        
        self.config = config or PipelineConfig()
        
        # 初始化各个模块
        self.query_processor = QueryProcessor()
        self.query_expander = MultiQueryExpander(llm_client, self.config.expansion_count)
        self.metadata_filter = MetadataFilter()
        self.hybrid_retriever = HybridRetriever(
            vector_service, 
            keyword_service,
            self.config.retrieval_weights,
            self.config.fusion_strategy
        )
        self.reranker = Reranker(cross_encoder_client, self.config.rerank_strategy)
        
        # 流水线统计
        self.pipeline_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_processing_time": 0.0,
            "stage_performance": {}
        }
    
    async def retrieve(self, query: str, kb_ids: List[str], 
                      user_context: Dict[str, Any] = None) -> PipelineResult:
        """执行增强检索流水线"""
        start_time = time.time()
        original_query = query
        
        try:
            logger.info(f"开始增强检索流水线，查询: {query}")
            
            # 初始化结果
            stage_results = {}
            expanded_queries = [query]
            retrieved_documents = []
            reranked_documents = []
            final_documents = []
            
            # 1. 查询预处理
            if self.config.enable_query_preprocessing:
                query, preprocessing_stats = await self._stage_query_preprocessing(query, user_context)
                stage_results[PipelineStage.QUERY_PREPROCESSING] = preprocessing_stats
            
            # 2. 查询扩展
            if self.config.enable_query_expansion:
                expanded_queries, expansion_stats = await self._stage_query_expansion(query, user_context)
                stage_results[PipelineStage.QUERY_EXPANSION] = expansion_stats
            
            # 3. 混合检索
            if self.config.enable_hybrid_retrieval:
                retrieved_documents, retrieval_stats = await self._stage_hybrid_retrieval(
                    expanded_queries, kb_ids
                )
                stage_results[PipelineStage.HYBRID_RETRIEVAL] = retrieval_stats
            
            # 4. 元数据过滤
            if self.config.enable_metadata_filtering and retrieved_documents:
                filtered_documents, filtering_stats = await self._stage_metadata_filtering(
                    retrieved_documents
                )
                stage_results[PipelineStage.METADATA_FILTERING] = filtering_stats
                retrieved_documents = filtered_documents
            
            # 5. 重排序
            if self.config.enable_reranking and retrieved_documents:
                reranked_documents, reranking_stats = await self._stage_reranking(
                    query, retrieved_documents
                )
                stage_results[PipelineStage.RERANKING] = reranking_stats
            else:
                # 如果没有重排序，将检索结果转换为重排序结果格式
                reranked_documents = self._convert_to_rerank_results(retrieved_documents)
            
            # 6. 后处理
            final_documents, post_processing_stats = await self._stage_post_processing(
                reranked_documents
            )
            stage_results[PipelineStage.POST_PROCESSING] = post_processing_stats
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 构建最终结果
            result = PipelineResult(
                query=query,
                original_query=original_query,
                expanded_queries=expanded_queries,
                retrieved_documents=retrieved_documents,
                reranked_documents=reranked_documents,
                final_documents=final_documents,
                pipeline_stats=self._calculate_pipeline_stats(stage_results, processing_time),
                stage_results=stage_results,
                processing_time=processing_time
            )
            
            # 更新统计信息
            self._update_pipeline_stats(result)
            
            logger.info(f"增强检索流水线完成，处理时间: {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"增强检索流水线失败: {e}")
            processing_time = time.time() - start_time
            
            # 返回降级结果
            return PipelineResult(
                query=query,
                original_query=original_query,
                expanded_queries=[query],
                retrieved_documents=[],
                reranked_documents=[],
                final_documents=[],
                pipeline_stats={"error": str(e)},
                stage_results={},
                processing_time=processing_time
            )
    
    async def _stage_query_preprocessing(self, query: str, user_context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """查询预处理阶段"""
        try:
            start_time = time.time()
            
            # 执行查询预处理
            processed_query = await self.query_processor.preprocess_query(query, user_context)
            
            processing_time = time.time() - start_time
            
            stats = {
                "original_query": query,
                "processed_query": processed_query,
                "processing_time": processing_time,
                "query_type": self.query_processor.analyze_query_type(query).value,
                "preprocessing_rules_applied": self.config.query_preprocessing_rules or []
            }
            
            return processed_query, stats
            
        except Exception as e:
            logger.error(f"查询预处理失败: {e}")
            return query, {"error": str(e)}
    
    async def _stage_query_expansion(self, query: str, user_context: Dict[str, Any]) -> Tuple[List[str], Dict[str, Any]]:
        """查询扩展阶段"""
        try:
            start_time = time.time()
            
            # 执行查询扩展
            expanded_queries = await self.query_expander.expand_query(
                query, 
                context=user_context.get("context") if user_context else None,
                strategy=self.config.expansion_strategy
            )
            
            processing_time = time.time() - start_time
            
            stats = {
                "original_query": query,
                "expanded_queries": expanded_queries,
                "expansion_count": len(expanded_queries),
                "expansion_strategy": self.config.expansion_strategy.value,
                "processing_time": processing_time,
                "expansion_stats": self.query_expander.get_expansion_stats(query)
            }
            
            return expanded_queries, stats
            
        except Exception as e:
            logger.error(f"查询扩展失败: {e}")
            return [query], {"error": str(e)}
    
    async def _stage_hybrid_retrieval(self, queries: List[str], kb_ids: List[str]) -> Tuple[List[Dict], Dict[str, Any]]:
        """混合检索阶段"""
        try:
            start_time = time.time()
            
            if self.config.enable_parallel_processing and len(queries) > 1:
                # 并行检索
                retrieval_tasks = []
                for query in queries:
                    task = self.hybrid_retriever.retrieve(
                        query, kb_ids, self.config.max_retrieval_results
                    )
                    retrieval_tasks.append(task)
                
                all_results = await asyncio.gather(*retrieval_tasks, return_exceptions=True)
                
                # 合并结果
                retrieved_documents = []
                for i, result in enumerate(all_results):
                    if isinstance(result, Exception):
                        logger.error(f"查询 {queries[i]} 检索失败: {result}")
                        continue
                    retrieved_documents.extend(result)
                
                # 去重
                retrieved_documents = self._deduplicate_documents(retrieved_documents)
                
            else:
                # 串行检索
                retrieved_documents = []
                for query in queries:
                    result = await self.hybrid_retriever.retrieve(
                        query, kb_ids, self.config.max_retrieval_results
                    )
                    retrieved_documents.extend(result)
                
                # 去重
                retrieved_documents = self._deduplicate_documents(retrieved_documents)
            
            processing_time = time.time() - start_time
            
            stats = {
                "queries_count": len(queries),
                "retrieved_documents_count": len(retrieved_documents),
                "processing_time": processing_time,
                "fusion_strategy": self.config.fusion_strategy.value,
                "retrieval_stats": self.hybrid_retriever.get_retrieval_stats(queries[0], retrieved_documents)
            }
            
            return retrieved_documents, stats
            
        except Exception as e:
            logger.error(f"混合检索失败: {e}")
            return [], {"error": str(e)}
    
    async def _stage_metadata_filtering(self, documents: List[Dict]) -> Tuple[List[Dict], Dict[str, Any]]:
        """元数据过滤阶段"""
        try:
            start_time = time.time()
            
            # 执行元数据过滤
            filtered_documents = await self.metadata_filter.filter_documents(
                documents,
                conditions=self.config.custom_conditions,
                predefined_filters=self.config.predefined_filters
            )
            
            processing_time = time.time() - start_time
            
            stats = {
                "original_count": len(documents),
                "filtered_count": len(filtered_documents),
                "processing_time": processing_time,
                "filter_stats": self.metadata_filter.get_filter_stats(len(documents), len(filtered_documents)),
                "applied_filters": self.config.predefined_filters or [],
                "custom_conditions": [str(cond) for cond in (self.config.custom_conditions or [])]
            }
            
            return filtered_documents, stats
            
        except Exception as e:
            logger.error(f"元数据过滤失败: {e}")
            return documents, {"error": str(e)}
    
    async def _stage_reranking(self, query: str, documents: List[Dict]) -> Tuple[List[RerankResult], Dict[str, Any]]:
        """重排序阶段"""
        try:
            start_time = time.time()
            
            # 执行重排序
            reranked_documents = await self.reranker.rerank(
                query, documents, self.config.rerank_top_k
            )
            
            processing_time = time.time() - start_time
            
            stats = {
                "original_count": len(documents),
                "reranked_count": len(reranked_documents),
                "processing_time": processing_time,
                "rerank_strategy": self.config.rerank_strategy.value,
                "rerank_stats": self.reranker.get_rerank_stats(reranked_documents)
            }
            
            return reranked_documents, stats
            
        except Exception as e:
            logger.error(f"重排序失败: {e}")
            return self._convert_to_rerank_results(documents), {"error": str(e)}
    
    async def _stage_post_processing(self, reranked_documents: List[RerankResult]) -> Tuple[List[Dict], Dict[str, Any]]:
        """后处理阶段"""
        try:
            start_time = time.time()
            
            # 转换为最终格式
            final_documents = []
            for result in reranked_documents[:self.config.final_top_k]:
                final_documents.append({
                    "id": result.id,
                    "content": result.content,
                    "score": result.final_score,
                    "source_file": result.source_file,
                    "knowledge_base_id": result.knowledge_base_id,
                    "metadata": result.metadata,
                    "rerank_reason": result.rerank_reason,
                    "original_score": result.original_score,
                    "rerank_score": result.rerank_score
                })
            
            processing_time = time.time() - start_time
            
            stats = {
                "input_count": len(reranked_documents),
                "output_count": len(final_documents),
                "processing_time": processing_time,
                "final_top_k": self.config.final_top_k
            }
            
            return final_documents, stats
            
        except Exception as e:
            logger.error(f"后处理失败: {e}")
            return [], {"error": str(e)}
    
    def _deduplicate_documents(self, documents: List[Dict]) -> List[Dict]:
        """去重文档"""
        seen_ids = set()
        unique_documents = []
        
        for doc in documents:
            doc_id = doc.get("id")
            if doc_id and doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_documents.append(doc)
        
        return unique_documents
    
    def _convert_to_rerank_results(self, documents: List[Dict]) -> List[RerankResult]:
        """将文档转换为重排序结果格式"""
        rerank_results = []
        for doc in documents:
            score = doc.get("score", 0.0)
            rerank_results.append(RerankResult(
                id=doc["id"],
                content=doc["content"],
                original_score=score,
                rerank_score=score,
                final_score=score,
                source_file=doc.get("source_file", ""),
                knowledge_base_id=doc.get("knowledge_base_id", ""),
                metadata=doc.get("metadata", {}),
                rerank_reason="no_reranking"
            ))
        return rerank_results
    
    def _calculate_pipeline_stats(self, stage_results: Dict[str, Any], processing_time: float) -> Dict[str, Any]:
        """计算流水线统计信息"""
        stats = {
            "total_processing_time": processing_time,
            "stages_completed": len(stage_results),
            "stages_failed": 0,
            "stage_performance": {}
        }
        
        for stage, result in stage_results.items():
            if "error" in result:
                stats["stages_failed"] += 1
            else:
                stage_time = result.get("processing_time", 0.0)
                stats["stage_performance"][stage] = {
                    "processing_time": stage_time,
                    "percentage": (stage_time / processing_time * 100) if processing_time > 0 else 0
                }
        
        return stats
    
    def _update_pipeline_stats(self, result: PipelineResult):
        """更新流水线统计信息"""
        self.pipeline_stats["total_queries"] += 1
        
        if result.final_documents:
            self.pipeline_stats["successful_queries"] += 1
        else:
            self.pipeline_stats["failed_queries"] += 1
        
        # 更新平均处理时间
        total_time = self.pipeline_stats["avg_processing_time"] * (self.pipeline_stats["total_queries"] - 1)
        total_time += result.processing_time
        self.pipeline_stats["avg_processing_time"] = total_time / self.pipeline_stats["total_queries"]
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """获取流水线统计信息"""
        return self.pipeline_stats.copy()
    
    def update_config(self, config: PipelineConfig):
        """更新流水线配置"""
        self.config = config
        
        # 更新子模块配置
        self.query_expander.expansion_count = config.expansion_count
        self.hybrid_retriever.fusion_strategy = config.fusion_strategy
        if config.retrieval_weights:
            self.hybrid_retriever.weights = config.retrieval_weights
        self.reranker.strategy = config.rerank_strategy 