"""
增强检索功能测试
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock

from app.services.query_processor import QueryProcessor
from app.services.multi_query_expander import QueryType
from app.services.multi_query_expander import MultiQueryExpander, ExpansionStrategy
from app.services.hybrid_retriever import HybridRetriever, FusionStrategy
from app.services.reranker import Reranker, RerankStrategy
from app.services.metadata_filter import MetadataFilter, FilterCondition, FilterOperator
from app.services.enhanced_retrieval_pipeline import EnhancedRetrievalPipeline, PipelineConfig


class TestQueryProcessor:
    """查询处理器测试"""
    
    def test_analyze_query_type(self):
        processor = QueryProcessor()
        
        # 测试问题性查询
        assert processor.analyze_query_type("如何安装Python") == QueryType.QUESTION
        assert processor.analyze_query_type("为什么使用React") == QueryType.QUESTION
        
        # 测试指令性查询
        assert processor.analyze_query_type("安装Docker") == QueryType.INSTRUCTION
        assert processor.analyze_query_type("配置数据库") == QueryType.INSTRUCTION
        
        # 测试概念性查询
        assert processor.analyze_query_type("什么是机器学习") == QueryType.CONCEPTUAL
        assert processor.analyze_query_type("定义API") == QueryType.CONCEPTUAL
        
        # 测试事实性查询
        assert processor.analyze_query_type("Python版本信息") == QueryType.FACTUAL
    
    def test_preprocess_query(self):
        processor = QueryProcessor()
        
        # 测试基本预处理
        result = asyncio.run(processor.preprocess_query("如何  安装  Python?"))
        assert "如何安装Python" in result
        
        # 测试特殊字符处理
        result = asyncio.run(processor.preprocess_query("Python@#$%安装"))
        assert "Python安装" in result


class TestMultiQueryExpander:
    """多查询扩展器测试"""
    
    def test_synonym_expansion(self):
        expander = MultiQueryExpander()
        
        # 测试同义词扩展
        expansions = expander._synonym_expansion("python安装")
        assert len(expansions) > 0
        assert any("python" in exp for exp in expansions)
    
    def test_concept_expansion(self):
        expander = MultiQueryExpander()
        
        # 测试概念扩展
        expansions = expander._concept_expansion("机器学习教程")
        assert len(expansions) > 0
    
    def test_question_expansion(self):
        expander = MultiQueryExpander()
        
        # 测试问题形式扩展
        expansions = expander._question_expansion("安装Docker")
        assert len(expansions) > 0
        assert any("如何" in exp for exp in expansions)


class TestMetadataFilter:
    """元数据过滤器测试"""
    
    def test_exact_match_filter(self):
        filter_instance = MetadataFilter()
        
        documents = [
            {"id": "1", "content": "test", "metadata": {"source_type": "official_doc"}},
            {"id": "2", "content": "test", "metadata": {"source_type": "blog"}}
        ]
        
        condition = FilterCondition("source_type", FilterOperator.EQUALS, "official_doc")
        result = asyncio.run(filter_instance.filter_documents(documents, [condition]))
        
        assert len(result) == 1
        assert result[0]["id"] == "1"
    
    def test_predefined_filters(self):
        filter_instance = MetadataFilter()
        
        documents = [
            {"id": "1", "content": "test", "metadata": {"quality_score": 0.8}},
            {"id": "2", "content": "test", "metadata": {"quality_score": 0.5}}
        ]
        
        result = asyncio.run(filter_instance.filter_documents(
            documents, predefined_filters=["high_quality"]
        ))
        
        assert len(result) == 1
        assert result[0]["id"] == "1"


class TestReranker:
    """重排序器测试"""
    
    def test_rule_based_rerank(self):
        reranker = Reranker(strategy=RerankStrategy.RULE_BASED)
        
        documents = [
            {"id": "1", "content": "Python安装教程", "score": 0.8},
            {"id": "2", "content": "普通文档", "score": 0.9}
        ]
        
        result = asyncio.run(reranker.rerank("Python安装", documents))
        
        assert len(result) == 2
        # 包含"Python"的文档应该获得更高的重排序分数
        assert result[0].rerank_score > result[1].rerank_score
    
    def test_exact_match_calculation(self):
        reranker = Reranker()
        
        score = reranker._calculate_exact_match("Python安装", "Python安装教程")
        assert score > 0.5  # 应该有较高的匹配分数
        
        score = reranker._calculate_exact_match("Python安装", "普通文档")
        assert score < 0.5  # 应该有较低的匹配分数


class TestHybridRetriever:
    """混合检索器测试"""
    
    def test_weighted_sum_fusion(self):
        # 模拟向量服务
        mock_vector_service = Mock()
        mock_vector_service.hybrid_search = AsyncMock(return_value={
            "text": [
                {"id": "1", "content": "test1", "score": 0.8, "source_file": "", "knowledge_base_id": "", "metadata": {}}
            ]
        })
        
        retriever = HybridRetriever(
            vector_service=mock_vector_service,
            weights={"vector": 0.7, "keyword": 0.3}
        )
        
        result = asyncio.run(retriever.retrieve("test", ["kb1"]))
        
        assert len(result) > 0
        assert "fused_score" in result[0]


class TestEnhancedRetrievalPipeline:
    """增强检索流水线测试"""
    
    def test_pipeline_initialization(self):
        config = PipelineConfig(
            enable_query_preprocessing=True,
            enable_query_expansion=True,
            expansion_strategy=ExpansionStrategy.HYBRID,
            expansion_count=3,
            enable_metadata_filtering=True,
            enable_hybrid_retrieval=True,
            fusion_strategy=FusionStrategy.WEIGHTED_SUM,
            enable_reranking=True,
            rerank_strategy=RerankStrategy.HYBRID,
            rerank_top_k=20,
            max_retrieval_results=50,
            final_top_k=10,
            enable_parallel_processing=True
        )
        
        # 模拟向量服务
        mock_vector_service = Mock()
        mock_vector_service.hybrid_search = AsyncMock(return_value={
            "text": [
                {"id": "1", "content": "test1", "score": 0.8, "source_file": "", "knowledge_base_id": "", "metadata": {}}
            ]
        })
        
        pipeline = EnhancedRetrievalPipeline(
            vector_service=mock_vector_service,
            config=config
        )
        
        assert pipeline.config.enable_query_preprocessing == True
        assert pipeline.config.expansion_strategy == ExpansionStrategy.HYBRID
        assert pipeline.config.fusion_strategy == FusionStrategy.WEIGHTED_SUM
    
    def test_pipeline_stats(self):
        pipeline = EnhancedRetrievalPipeline()
        
        stats = pipeline.get_pipeline_stats()
        
        assert "total_queries" in stats
        assert "successful_queries" in stats
        assert "failed_queries" in stats
        assert "avg_processing_time" in stats


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 