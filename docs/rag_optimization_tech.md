# MetaBox RAG优化技术实现方案

## 📋 技术背景

基于对Dify和LangChain技术点的深入分析，MetaBox将实现一套完整的RAG优化技术栈，提升检索精度和用户体验。

## 🎯 核心技术实现

### 1. 智能文档分割与向量化配置系统

#### 1.1 文档类型智能检测
```python
class DocumentTypeDetector:
    """文档类型智能检测器"""
    def __init__(self):
        self.type_patterns = {
            "markdown": [r"^#\s+", r"^##\s+", r"^###\s+"],
            "code": [r"```[\w]*\n", r"import\s+", r"def\s+", r"class\s+"],
            "technical": [r"API", r"接口", r"参数", r"配置"],
            "academic": [r"摘要", r"Abstract", r"参考文献", r"References"],
            "news": [r"本报讯", r"记者", r"时间", r"地点"],
            "manual": [r"使用说明", r"操作步骤", r"注意事项", r"FAQ"]
        }
    
    def detect_document_type(self, text: str) -> Dict[str, float]:
        """检测文档类型及置信度"""
        scores = {}
        for doc_type, patterns in self.type_patterns.items():
            score = sum(len(re.findall(pattern, text)) for pattern in patterns)
            scores[doc_type] = score / len(text) * 1000  # 归一化
        return scores
    
    def get_primary_type(self, text: str) -> str:
        """获取主要文档类型"""
        scores = self.detect_document_type(text)
        return max(scores.items(), key=lambda x: x[1])[0]
```

#### 1.2 智能参数推荐引擎
```python
class SmartParameterRecommender:
    """智能参数推荐引擎"""
    def __init__(self):
        self.recommendations = {
            "markdown": {
                "splitter": "markdown_header",
                "chunk_size": 512,
                "chunk_overlap": 64,
                "embedding_model": "bge-m3",
                "use_parent_child": True
            },
            "code": {
                "splitter": "recursive",
                "chunk_size": 256,
                "chunk_overlap": 32,
                "embedding_model": "code-embedding-model",
                "use_parent_child": False
            },
            "technical": {
                "splitter": "recursive",
                "chunk_size": 384,
                "chunk_overlap": 48,
                "embedding_model": "bge-m3",
                "use_parent_child": True
            },
            "academic": {
                "splitter": "semantic",
                "chunk_size": 768,
                "chunk_overlap": 96,
                "embedding_model": "bge-m3",
                "use_parent_child": True
            },
            "news": {
                "splitter": "recursive",
                "chunk_size": 256,
                "chunk_overlap": 32,
                "embedding_model": "text-embedding-ada-002",
                "use_parent_child": False
            },
            "manual": {
                "splitter": "markdown_header",
                "chunk_size": 384,
                "chunk_overlap": 48,
                "embedding_model": "bge-m3",
                "use_parent_child": True
            }
        }
    
    def get_recommendation(self, doc_type: str, text_length: int = 0) -> Dict[str, Any]:
        """获取参数推荐"""
        base_config = self.recommendations.get(doc_type, self.recommendations["technical"])
        
        # 根据文本长度调整参数
        if text_length > 10000:
            base_config["chunk_size"] = min(base_config["chunk_size"] * 1.5, 1024)
            base_config["chunk_overlap"] = min(base_config["chunk_overlap"] * 1.2, 128)
        elif text_length < 1000:
            base_config["chunk_size"] = max(base_config["chunk_size"] * 0.7, 128)
            base_config["chunk_overlap"] = max(base_config["chunk_overlap"] * 0.8, 16)
        
        return base_config
```

#### 1.3 智能配置管理器
```python
class SmartConfigManager:
    """智能配置管理器"""
    def __init__(self):
        self.type_detector = DocumentTypeDetector()
        self.param_recommender = SmartParameterRecommender()
    
    def get_smart_config(self, text: str, user_preferences: Dict = None) -> Dict[str, Any]:
        """获取智能配置"""
        # 检测文档类型
        doc_type = self.type_detector.get_primary_type(text)
        
        # 获取推荐参数
        config = self.param_recommender.get_recommendation(doc_type, len(text))
        
        # 应用用户偏好
        if user_preferences:
            config.update(user_preferences)
        
        # 添加元数据
        config["detected_type"] = doc_type
        config["confidence"] = self.type_detector.detect_document_type(text)[doc_type]
        
        return config
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """验证配置参数"""
        errors = []
        
        if config.get("chunk_size", 0) <= 0:
            errors.append("chunk_size 必须大于0")
        
        if config.get("chunk_overlap", 0) >= config.get("chunk_size", 1):
            errors.append("chunk_overlap 必须小于 chunk_size")
        
        if config.get("chunk_overlap", 0) < 0:
            errors.append("chunk_overlap 不能为负数")
        
        return len(errors) == 0, errors
```

### 2. 高级文本分割技术

#### 2.1 RecursiveCharacterTextSplitter
```python
class RecursiveCharacterTextSplitter:
    """递归字符分割器"""
    def __init__(self, chunk_size=512, chunk_overlap=64, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "！", "？", "；", " ", ""]
    
    def split_text(self, text: str) -> List[str]:
        """递归分割文本"""
        if not text.strip():
            return []
        
        # 尝试按不同分隔符分割
        for separator in self.separators:
            if separator in text:
                splits = self._split_text_with_separator(text, separator)
                if len(splits) > 1:
                    return self._merge_splits(splits)
        
        # 如果没有找到合适的分隔符，按字符分割
        return self._split_text_by_characters(text)
    
    def _split_text_with_separator(self, text: str, separator: str) -> List[str]:
        """使用指定分隔符分割文本"""
        if separator == "":
            return list(text)
        
        splits = text.split(separator)
        return [s + separator for s in splits[:-1]] + [splits[-1]]
    
    def _merge_splits(self, splits: List[str]) -> List[str]:
        """合并分割结果，确保块大小合适"""
        merged_splits = []
        current_chunk = ""
        
        for split in splits:
            if len(current_chunk) + len(split) > self.chunk_size and current_chunk:
                merged_splits.append(current_chunk.strip())
                
                if self.chunk_overlap > 0:
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + split
                else:
                    current_chunk = split
            else:
                current_chunk += split
        
        if current_chunk.strip():
            merged_splits.append(current_chunk.strip())
        
        return merged_splits
    
    def _split_text_by_characters(self, text: str) -> List[str]:
        """按字符分割文本"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk.strip():
                chunks.append(chunk.strip())
        return chunks
```

#### 2.2 MarkdownHeaderTextSplitter
```python
class MarkdownHeaderTextSplitter:
    """Markdown标题分割器"""
    def __init__(self, headers_to_split_on=None):
        self.headers_to_split_on = headers_to_split_on or [
            ("#", "标题1"),
            ("##", "标题2"),
            ("###", "标题3"),
            ("####", "标题4"),
            ("#####", "标题5"),
            ("######", "标题6"),
        ]
        
        # 构建正则表达式模式
        self.header_patterns = []
        for header, name in self.headers_to_split_on:
            pattern = rf"^{re.escape(header)}\s+(.+)$"
            self.header_patterns.append((pattern, name, len(header)))
    
    def split_text(self, text: str) -> List[TextChunk]:
        """按Markdown标题分割文本"""
        lines = text.split('\n')
        chunks = []
        current_chunk = ""
        current_header = ""
        current_level = 0
        
        for line in lines:
            header_info = self._is_header_line(line)
            
            if header_info:
                if current_chunk.strip():
                    chunks.append(TextChunk(
                        content=current_chunk.strip(),
                        metadata={
                            "splitter": "markdown_header",
                            "header": current_header,
                            "level": current_level
                        }
                    ))
                
                current_header = header_info["title"]
                current_level = header_info["level"]
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
        
        if current_chunk.strip():
            chunks.append(TextChunk(
                content=current_chunk.strip(),
                metadata={
                    "splitter": "markdown_header",
                    "header": current_header,
                    "level": current_level
                }
            ))
        
        return chunks
    
    def _is_header_line(self, line: str) -> Optional[Dict[str, Any]]:
        """检查是否是标题行"""
        for pattern, name, level in self.header_patterns:
            match = re.match(pattern, line.strip())
            if match:
                return {
                    "title": match.group(1).strip(),
                    "level": level,
                    "name": name
                }
        return None
```

#### 2.3 ParentChildTextSplitter
```python
class ParentChildTextSplitter:
    """父子块分割器"""
    def __init__(self, parent_chunk_size=1024, child_chunk_size=256, child_overlap=32):
        self.parent_chunk_size = parent_chunk_size
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=64
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_overlap
        )
    
    def split_text(self, text: str) -> List[TextChunk]:
        """生成父子块结构"""
        parent_chunks = self.recursive_splitter.split_text(text)
        
        all_chunks = []
        chunk_id_counter = 0
        
        for parent_chunk in parent_chunks:
            parent_id = f"parent_{chunk_id_counter}"
            chunk_id_counter += 1
            
            # 添加父块
            parent_chunk_obj = TextChunk(
                content=parent_chunk,
                metadata={
                    "splitter": "parent_child",
                    "chunk_type": "parent",
                    "parent_id": None,
                    "chunk_id": parent_id
                }
            )
            all_chunks.append(parent_chunk_obj)
            
            # 生成子块
            child_chunks = self.child_splitter.split_text(parent_chunk)
            
            for i, child_chunk in enumerate(child_chunks):
                child_id = f"child_{chunk_id_counter}_{i}"
                child_chunk_obj = TextChunk(
                    content=child_chunk,
                    metadata={
                        "splitter": "parent_child",
                        "chunk_type": "child",
                        "parent_id": parent_id,
                        "child_index": i,
                        "chunk_id": child_id
                    }
                )
                all_chunks.append(child_chunk_obj)
        
        return all_chunks
```

### 3. 多模型Embedding路由

#### 3.1 EmbeddingRouter
```python
class EmbeddingRouter:
    """多模型Embedding路由"""
    def __init__(self):
        self.models = {
            "long_text": "bge-m3",
            "short_text": "text-embedding-ada-002",
            "code": "code-embedding-model",
            "technical": "bge-m3",
            "academic": "bge-m3",
            "news": "text-embedding-ada-002"
        }
    
    def get_embedding(self, text: str, text_type: str = "auto") -> List[float]:
        """根据文本类型选择模型"""
        if text_type == "auto":
            text_type = self._detect_text_type(text)
        
        model_name = self.models.get(text_type, "bge-m3")
        return self._get_embedding_from_model(text, model_name)
    
    def _detect_text_type(self, text: str) -> str:
        """自动检测文本类型"""
        if len(text) > 1000:
            return "long_text"
        elif len(text) < 100:
            return "short_text"
        else:
            return "technical"
    
    def _get_embedding_from_model(self, text: str, model_name: str) -> List[float]:
        """从指定模型获取embedding"""
        # 这里应该调用实际的embedding服务
        pass
```

#### 3.2 HybridEmbedding
```python
class HybridEmbedding:
    """父子联合Embedding"""
    def __init__(self, parent_weight=0.3, child_weight=0.7):
        self.parent_weight = parent_weight
        self.child_weight = child_weight
    
    def get_hybrid_embedding(self, parent_text: str, child_text: str) -> List[float]:
        """生成父子联合向量"""
        parent_embedding = self._get_embedding(parent_text)
        child_embedding = self._get_embedding(child_text)
        
        # 加权平均
        hybrid_embedding = []
        for p, c in zip(parent_embedding, child_embedding):
            hybrid_embedding.append(p * self.parent_weight + c * self.child_weight)
        
        return hybrid_embedding
    
    def _get_embedding(self, text: str) -> List[float]:
        """获取文本embedding"""
        # 调用embedding服务
        pass
```

### 4. 混合检索引擎

#### 4.1 HybridRetriever
```python
class HybridRetriever:
    """混合检索器"""
    def __init__(self, vector_weight=0.7, keyword_weight=0.3):
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
    
    async def retrieve(self, query: str, kb_ids: List[str], top_k: int = 10) -> List[Dict]:
        """混合检索"""
        # 向量检索
        vector_results = await self._vector_search(query, kb_ids, top_k)
        
        # 关键词检索
        keyword_results = await self._keyword_search(query, kb_ids, top_k)
        
        # 结果融合
        return self._merge_results(vector_results, keyword_results)
    
    async def _vector_search(self, query: str, kb_ids: List[str], top_k: int) -> List[Dict]:
        """向量检索"""
        pass
    
    async def _keyword_search(self, query: str, kb_ids: List[str], top_k: int) -> List[Dict]:
        """关键词检索"""
        pass
    
    def _merge_results(self, vector_results: List[Dict], keyword_results: List[Dict]) -> List[Dict]:
        """融合检索结果"""
        pass
```

#### 4.2 MultiQueryExpander
```python
class MultiQueryExpander:
    """多查询扩展器"""
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def expand_query(self, query: str, num_expansions: int = 3) -> List[str]:
        """扩展查询"""
        prompt = f"""
        请为以下查询生成{num_expansions}个不同的表达方式，保持语义相似但用词不同：
        
        原始查询：{query}
        
        请生成：
        """
        
        response = await self.llm_client.generate(prompt)
        expansions = self._parse_expansions(response)
        
        return [query] + expansions[:num_expansions-1]
    
    def _parse_expansions(self, response: str) -> List[str]:
        """解析扩展结果"""
        # 解析LLM返回的扩展查询
        pass
```

#### 4.3 Reranker
```python
class Reranker:
    """重排序器"""
    def __init__(self, model_name="bge-reranker-v2-m3"):
        self.model_name = model_name
    
    async def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        """重排序文档"""
        # 使用cross-encoder模型重排序
        pass
```

### 5. 元数据过滤系统

#### 5.1 MetadataFilter
```python
class MetadataFilter:
    """元数据过滤器"""
    def __init__(self):
        self.filters = {}
    
    def add_filter(self, field: str, value: Any, operator: str = "eq"):
        """添加过滤条件"""
        self.filters[field] = {"value": value, "operator": operator}
    
    def apply_filters(self, documents: List[Dict]) -> List[Dict]:
        """应用过滤条件"""
        filtered_docs = documents
        
        for field, filter_info in self.filters.items():
            value = filter_info["value"]
            operator = filter_info["operator"]
            
            if operator == "eq":
                filtered_docs = [doc for doc in filtered_docs if doc.get(field) == value]
            elif operator == "in":
                filtered_docs = [doc for doc in filtered_docs if doc.get(field) in value]
            elif operator == "gt":
                filtered_docs = [doc for doc in filtered_docs if doc.get(field, 0) > value]
            elif operator == "lt":
                filtered_docs = [doc for doc in filtered_docs if doc.get(field, 0) < value]
        
        return filtered_docs
```

## 🔄 优化Pipeline流程

### 智能处理流程
```
文档输入 
    ↓
智能文档类型检测
    ↓
智能参数推荐
    ↓
用户配置确认/调整
    ↓
Markdown Header 分块 (如果适用)
    ↓
Recursive 分块
    ↓
Parent-Child 结构生成 (如果启用)
    ↓
多模型Embedding路由
    ↓
父子联合向量化 (如果启用)
    ↓
向量库入库 + Metadata
    ↓
查询 Multi-query 扩展
    ↓
Hybrid Retrieval
    ↓
Metadata Filter
    ↓
Reranker 重排序
    ↓
Top-k 结果返回
```

## 🎨 用户界面设计

### 1. 智能配置界面
```typescript
interface SmartConfigPanel {
  // 文档类型检测结果
  detectedType: string;
  confidence: number;
  
  // 推荐配置
  recommendedConfig: {
    splitter: string;
    chunkSize: number;
    chunkOverlap: number;
    embeddingModel: string;
    useParentChild: boolean;
  };
  
  // 用户自定义配置
  customConfig: {
    enabled: boolean;
    splitter: string;
    chunkSize: number;
    chunkOverlap: number;
    embeddingModel: string;
    useParentChild: boolean;
    parentChunkSize: number;
    childChunkSize: number;
  };
  
  // 高级选项
  advancedOptions: {
    separators: string[];
    headerLevels: number[];
    semanticThreshold: number;
  };
}
```

### 2. 配置预览功能
- **实时预览**: 显示分割结果预览
- **参数调整**: 滑块和输入框调整参数
- **效果对比**: 不同配置的效果对比
- **性能预估**: 预估处理时间和存储需求

### 3. 批量配置管理
- **配置模板**: 保存常用配置为模板
- **批量应用**: 对多个文档应用相同配置
- **配置继承**: 子文档继承父文档配置
- **配置版本**: 配置变更历史记录

## 📊 性能优化指标

### 预期提升效果
- **检索精度**：提升15-25%
- **召回率**：提升20-30%
- **响应速度**：优化10-15%
- **用户体验**：显著改善
- **配置效率**：提升50-70%

### 技术指标
- **分块重叠率**：20-30%
- **向量维度**：1536维（兼容OpenAI）
- **检索数量**：Top-10 -> Rerank -> Top-5
- **缓存策略**：Redis缓存热点查询
- **配置准确率**：>85%

## 🛠️ 实现计划

### Phase 1: 智能配置系统 ✅
- [x] DocumentTypeDetector
- [x] SmartParameterRecommender
- [x] SmartConfigManager
- [x] 基础分割器实现

### Phase 2: 用户界面开发
- [ ] 智能配置面板
- [ ] 参数调整界面
- [ ] 预览功能
- [ ] 配置模板管理

### Phase 3: Embedding优化
- [ ] EmbeddingRouter
- [ ] HybridEmbedding
- [ ] 多模型集成

### Phase 4: 检索引擎
- [ ] HybridRetriever
- [ ] MultiQueryExpander
- [ ] Reranker

### Phase 5: 系统集成
- [ ] Pipeline整合
- [ ] 性能测试
- [ ] 用户界面优化

## 🔧 技术栈选择

### 核心依赖
- **文本分割**：自定义实现 + LangChain参考
- **向量模型**：bge-m3 + OpenAI + 本地模型
- **重排序**：bge-reranker-v2-m3
- **缓存**：Redis
- **数据库**：PostgreSQL + Qdrant

### 智能配置参数
```yaml
smart_config:
  # 文档类型检测
  type_detection:
    confidence_threshold: 0.6
    min_text_length: 100
    
  # 参数推荐
  recommendations:
    markdown:
      splitter: "markdown_header"
      chunk_size: 512
      chunk_overlap: 64
      embedding_model: "bge-m3"
      use_parent_child: true
    
    code:
      splitter: "recursive"
      chunk_size: 256
      chunk_overlap: 32
      embedding_model: "code-embedding-model"
      use_parent_child: false
    
    technical:
      splitter: "recursive"
      chunk_size: 384
      chunk_overlap: 48
      embedding_model: "bge-m3"
      use_parent_child: true
    
    academic:
      splitter: "semantic"
      chunk_size: 768
      chunk_overlap: 96
      embedding_model: "bge-m3"
      use_parent_child: true
    
    news:
      splitter: "recursive"
      chunk_size: 256
      chunk_overlap: 32
      embedding_model: "text-embedding-ada-002"
      use_parent_child: false
    
    manual:
      splitter: "markdown_header"
      chunk_size: 384
      chunk_overlap: 48
      embedding_model: "bge-m3"
      use_parent_child: true

  # 高级配置
  advanced:
    max_chunk_size: 1024
    min_chunk_size: 128
    max_overlap_ratio: 0.5
    semantic_threshold: 0.8
```

## 📈 监控与评估

### 关键指标
- **检索准确率**：Precision@K
- **召回率**：Recall@K
- **响应时间**：平均查询延迟
- **用户满意度**：反馈评分
- **配置准确率**：智能配置的准确性

### 评估方法
- **离线评估**：标准数据集测试
- **在线评估**：A/B测试
- **用户反馈**：满意度调查
- **配置验证**：配置推荐准确性测试

## 🚀 部署策略

### 渐进式部署
1. **灰度发布**：10%流量测试
2. **性能监控**：实时指标跟踪
3. **全量发布**：逐步扩大范围
4. **效果评估**：持续优化

### 回滚机制
- **快速回滚**：5分钟内回滚到稳定版本
- **数据备份**：定期备份向量库
- **监控告警**：异常情况及时通知

---

*本文档将随着实现进度持续更新* 