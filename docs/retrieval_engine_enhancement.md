# 抽取引擎提升技术文档

## 概述

本文档详细描述了MetaBox智能知识库系统的抽取引擎提升技术，包括多查询扩展、混合检索、重排序和元数据过滤等核心技术。

## 一、技术架构

### 1.1 整体架构

```
用户查询 -> 查询预处理 -> 多查询扩展 -> 混合检索 -> 重排序 -> 元数据过滤 -> 结果返回
```

### 1.2 核心组件

- **QueryProcessor**: 查询预处理和清洗
- **MultiQueryExpander**: 多查询扩展器
- **HybridRetriever**: 混合检索器
- **Reranker**: 重排序器
- **MetadataFilter**: 元数据过滤器
- **RetrievalPipeline**: 检索流水线

## 二、多查询扩展 (Multi-query Expansion)

### 2.1 技术原理

使用LLM将用户查询扩展成多个语义相似但表达不同的查询，提高检索召回率。

### 2.2 实现策略

```python
class MultiQueryExpander:
    """多查询扩展器"""
    
    def __init__(self, llm_client, expansion_count=3):
        self.llm_client = llm_client
        self.expansion_count = expansion_count
    
    async def expand_query(self, query: str, context: str = None) -> List[str]:
        """扩展查询"""
        # 1. 查询分析
        query_type = self._analyze_query_type(query)
        
        # 2. 生成扩展提示
        prompt = self._generate_expansion_prompt(query, query_type, context)
        
        # 3. LLM生成扩展查询
        expansions = await self._generate_expansions(prompt)
        
        # 4. 去重和过滤
        return self._deduplicate_queries([query] + expansions)
```

### 2.3 扩展策略

| 查询类型 | 扩展策略 | 示例 |
|---------|---------|------|
| 事实性查询 | 同义词替换、概念扩展 | "Python如何安装" -> "Python安装方法" |
| 概念性查询 | 相关概念、上下位词 | "机器学习" -> "人工智能"、"深度学习" |
| 问题性查询 | 问题重构、角度变换 | "为什么选择React" -> "React的优势" |

## 三、混合检索 (Hybrid Retrieval)

### 3.1 技术原理

结合向量检索和关键词检索的优势，通过加权融合提高检索精度和召回率。

### 3.2 实现架构

```python
class HybridRetriever:
    """混合检索器"""
    
    def __init__(self, vector_service, keyword_service, weights=None):
        self.vector_service = vector_service
        self.keyword_service = keyword_service
        self.weights = weights or {"vector": 0.7, "keyword": 0.3}
    
    async def retrieve(self, query: str, kb_ids: List[str], top_k: int = 10) -> List[Dict]:
        """混合检索"""
        # 1. 并行执行向量检索和关键词检索
        vector_results, keyword_results = await asyncio.gather(
            self._vector_search(query, kb_ids, top_k * 2),
            self._keyword_search(query, kb_ids, top_k * 2)
        )
        
        # 2. 结果融合
        merged_results = self._merge_results(vector_results, keyword_results)
        
        # 3. 去重和排序
        return self._deduplicate_and_sort(merged_results, top_k)
```

### 3.3 融合策略

1. **加权融合**: 根据检索类型分配权重
2. **交叉验证**: 同时出现在两种结果中的文档获得加分
3. **多样性保证**: 确保结果来源的多样性

## 四、重排序 (Rerank)

### 4.1 技术原理

使用Cross-Encoder模型对检索结果进行精确的相关性评分和重排序。

### 4.2 实现方案

```python
class Reranker:
    """重排序器"""
    
    def __init__(self, model_name="bge-reranker-v2-m3", batch_size=32):
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = self._load_model()
    
    async def rerank(self, query: str, documents: List[Dict], top_k: int = 5) -> List[Dict]:
        """重排序文档"""
        # 1. 准备重排序数据
        rerank_data = self._prepare_rerank_data(query, documents)
        
        # 2. 批量重排序
        scores = await self._batch_rerank(rerank_data)
        
        # 3. 更新文档分数
        reranked_docs = self._update_scores(documents, scores)
        
        # 4. 排序并返回top_k
        return sorted(reranked_docs, key=lambda x: x["rerank_score"], reverse=True)[:top_k]
```

### 4.3 重排序策略

1. **相关性评分**: 使用Cross-Encoder计算query-document相关性
2. **多样性重排**: 考虑文档间的相似性，避免重复
3. **上下文感知**: 考虑文档在知识库中的上下文关系

## 五、元数据过滤 (Metadata Filter)

### 5.1 技术原理

根据文档的元数据信息进行预过滤，提高检索效率和准确性。

### 5.2 实现方案

```python
class MetadataFilter:
    """元数据过滤器"""
    
    def __init__(self):
        self.filter_rules = self._load_filter_rules()
    
    def filter_documents(self, query: str, documents: List[Dict], 
                        filters: Dict[str, Any]) -> List[Dict]:
        """过滤文档"""
        # 1. 解析过滤条件
        filter_conditions = self._parse_filters(filters)
        
        # 2. 应用过滤规则
        filtered_docs = []
        for doc in documents:
            if self._apply_filters(doc, filter_conditions):
                filtered_docs.append(doc)
        
        # 3. 返回过滤结果
        return filtered_docs
```

### 5.3 过滤维度

| 过滤维度 | 描述 | 示例 |
|---------|------|------|
| 知识库ID | 指定检索的知识库范围 | kb_ids: ["kb1", "kb2"] |
| 文档类型 | 按文档类型过滤 | doc_types: ["markdown", "pdf"] |
| 时间范围 | 按创建/更新时间过滤 | date_range: ["2024-01-01", "2024-12-31"] |
| 标签 | 按标签过滤 | tags: ["技术文档", "API"] |

## 六、检索流水线 (Retrieval Pipeline)

### 6.1 流水线设计

```python
class RetrievalPipeline:
    """检索流水线"""
    
    def __init__(self, config: Dict[str, Any]):
        self.query_processor = QueryProcessor()
        self.query_expander = MultiQueryExpander(config.get("llm_client"))
        self.hybrid_retriever = HybridRetriever(
            config.get("vector_service"),
            config.get("keyword_service")
        )
        self.reranker = Reranker(config.get("rerank_model"))
        self.metadata_filter = MetadataFilter()
        
        # 流水线配置
        self.enable_expansion = config.get("enable_expansion", True)
        self.enable_rerank = config.get("enable_rerank", True)
        self.enable_filter = config.get("enable_filter", True)
    
    async def retrieve(self, query: str, kb_ids: List[str], 
                      filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict]:
        """执行检索流水线"""
        # 1. 查询预处理
        processed_query = await self.query_processor.process(query)
        
        # 2. 多查询扩展
        if self.enable_expansion:
            expanded_queries = await self.query_expander.expand_query(processed_query)
        else:
            expanded_queries = [processed_query]
        
        # 3. 混合检索
        all_results = []
        for exp_query in expanded_queries:
            results = await self.hybrid_retriever.retrieve(exp_query, kb_ids, top_k * 2)
            all_results.extend(results)
        
        # 4. 去重和合并
        merged_results = self._merge_and_deduplicate(all_results)
        
        # 5. 元数据过滤
        if self.enable_filter and filters:
            merged_results = self.metadata_filter.filter_documents(
                processed_query, merged_results, filters
            )
        
        # 6. 重排序
        if self.enable_rerank:
            final_results = await self.reranker.rerank(
                processed_query, merged_results[:top_k * 2], top_k
            )
        else:
            final_results = merged_results[:top_k]
        
        return final_results
```

### 6.2 性能优化

1. **并行处理**: 查询扩展和检索并行执行
2. **缓存机制**: 缓存查询扩展和检索结果
3. **批量处理**: 批量执行重排序操作
4. **早期终止**: 根据相关性阈值早期终止

## 七、配置和调优

### 7.1 配置参数

```yaml
retrieval_engine:
  # 多查询扩展配置
  query_expansion:
    enabled: true
    expansion_count: 3
    max_tokens: 1000
    temperature: 0.7
  
  # 混合检索配置
  hybrid_retrieval:
    vector_weight: 0.7
    keyword_weight: 0.3
    fusion_strategy: "weighted"
  
  # 重排序配置
  rerank:
    enabled: true
    model_name: "bge-reranker-v2-m3"
    batch_size: 32
    top_k_before_rerank: 20
  
  # 元数据过滤配置
  metadata_filter:
    enabled: true
    strict_mode: false
    fallback_to_all: true
```

### 7.2 性能调优

1. **查询扩展调优**: 根据查询类型调整扩展数量
2. **权重调优**: 根据数据特点调整向量和关键词权重
3. **重排序调优**: 根据性能要求调整重排序范围
4. **缓存调优**: 合理设置缓存TTL和大小

## 八、监控和评估

### 8.1 关键指标

- **检索准确率**: Precision@K
- **检索召回率**: Recall@K
- **响应时间**: 平均查询延迟
- **用户满意度**: 反馈评分
- **系统吞吐量**: QPS

### 8.2 评估方法

1. **离线评估**: 使用标准数据集进行测试
2. **在线评估**: A/B测试对比不同策略
3. **用户反馈**: 收集用户对检索结果的评价
4. **性能监控**: 实时监控系统性能指标

## 九、部署和运维

### 9.1 部署架构

```
用户请求 -> 负载均衡器 -> 检索服务集群 -> 向量数据库
                                    ↓
                              重排序服务 -> 模型服务
```

### 9.2 运维要点

1. **资源管理**: 合理分配CPU和内存资源
2. **并发控制**: 根据资源情况调整并发数
3. **故障处理**: 实现降级和重试机制
4. **监控告警**: 设置关键指标告警

## 十、未来规划

### 10.1 技术演进

1. **多模态检索**: 支持文本、图片、音频混合检索
2. **个性化检索**: 基于用户画像的个性化检索
3. **实时学习**: 根据用户反馈实时调整检索策略
4. **联邦检索**: 支持跨知识库的联邦检索

### 10.2 性能提升

1. **模型优化**: 使用更高效的检索和重排序模型
2. **架构优化**: 微服务化和容器化部署
3. **缓存优化**: 多级缓存策略
4. **算法优化**: 更智能的融合和排序算法

---

本文档为MetaBox智能知识库系统抽取引擎提升技术的完整设计参考，涵盖了多查询扩展、混合检索、重排序和元数据过滤等核心技术。后续可根据实际使用情况和性能表现进行持续优化。 