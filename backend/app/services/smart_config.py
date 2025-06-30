"""
智能配置服务
基于RAG优化技术实现的高级配置管理
"""
from typing import Dict, List, Optional, Tuple, Any
import re
import json
import time
import uuid
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

from app.schemas.smart_config import (
    DocumentType,
    SmartConfigRequest,
    SmartConfigResponse,
    ParameterRecommendation,
    ValidationResult,
    ConfigTemplate,
    ConfigTemplateCreate,
    ConfigTemplateUpdate,
    BatchConfigRequest,
    BatchConfigResponse,
    PerformanceMetrics,
    ConfigPreview,
    AdvancedConfig
)
from app.services.text_splitter import (
    TextSplitterFactory,
    DocumentTypeDetector as BaseDocumentTypeDetector,
    SmartParameterRecommender as BaseSmartParameterRecommender,
    SmartConfigManager as BaseSmartConfigManager
)
from app.services.advanced_preview import AdvancedPreviewService
from app.services.hybrid_chunker import HybridChunker
from app.services.embedding_router import EmbeddingRouter

logger = logging.getLogger(__name__)


class DocumentTypeDetector:
    """文档类型检测器"""
    
    def __init__(self):
        self.type_patterns = {
            DocumentType.CODE: [
                r'def\s+\w+', r'class\s+\w+', r'import\s+', r'from\s+', r'return\s+',
                r'if\s+__name__', r'try:', r'except:', r'for\s+', r'while\s+',
                r'function\s+', r'const\s+', r'let\s+', r'var\s+', r'public\s+class',
                r'private\s+', r'protected\s+', r'interface\s+', r'abstract\s+class'
            ],
            DocumentType.TECHNICAL: [
                r'API', r'endpoint', r'database', r'schema', r'table', r'column',
                r'configuration', r'setup', r'installation', r'deployment',
                r'接口', r'参数', r'配置', r'部署', r'安装', r'数据库', r'表结构'
            ],
            DocumentType.ACADEMIC: [
                r'abstract', r'introduction', r'methodology', r'conclusion',
                r'references', r'bibliography', r'figure', r'table', r'摘要',
                r'引言', r'方法', r'结论', r'参考文献', r'图表'
            ],
            DocumentType.NEWS: [
                r'breaking', r'news', r'report', r'announcement', r'press release',
                r'interview', r'exclusive', r'update', r'本报讯', r'记者',
                r'时间', r'地点', r'报道'
            ],
            DocumentType.LITERATURE: [
                r'chapter', r'scene', r'dialogue', r'character', r'plot',
                r'narrative', r'story', r'novel', r'章节', r'场景', r'对话',
                r'角色', r'情节', r'叙述'
            ],
            DocumentType.MARKDOWN: [
                r'^#\s+', r'^##\s+', r'^###\s+', r'^####\s+', r'^#####\s+',
                r'^######\s+', r'\*\*.*?\*\*', r'\*.*?\*', r'`.*?`', r'\[.*?\]\(.*?\)'
            ],
            DocumentType.MANUAL: [
                r'使用说明', r'操作步骤', r'注意事项', r'FAQ', r'常见问题',
                r'user guide', r'manual', r'tutorial', r'step by step',
                r'instructions', r'how to'
            ]
        }
    
    def detect_document_type(self, content: str) -> DocumentType:
        """检测文档类型"""
        content_lower = content.lower()
        scores = {}
        
        for doc_type, patterns in self.type_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches * 10  # 每个匹配加10分
            
            # 特殊规则
            if doc_type == DocumentType.CODE:
                # 代码文档通常有特定的缩进和结构
                code_lines = len([line for line in content.split('\n') 
                                if re.match(r'^\s*(def|class|import|from|if|for|while|try|except)', line)])
                if code_lines > len(content.split('\n')) * 0.1:  # 超过10%的代码行
                    score += 50
            
            elif doc_type == DocumentType.MARKDOWN:
                # Markdown文档有特定的标记
                markdown_indicators = ['#', '**', '*', '`', '[', ']', '![']
                if any(indicator in content for indicator in markdown_indicators):
                    score += 30
            
            scores[doc_type] = score
        
        # 返回得分最高的类型
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return DocumentType.GENERAL
    
    def get_confidence_score(self, content: str, doc_type: DocumentType) -> float:
        """获取类型置信度"""
        scores = {}
        for dt, patterns in self.type_patterns.items():
            score = sum(len(re.findall(pattern, content, re.IGNORECASE)) for pattern in patterns)
            scores[dt] = score
        
        total_score = sum(scores.values())
        if total_score == 0:
            return 0.5  # 默认置信度
        
        return min(1.0, scores.get(doc_type, 0) / total_score * 2)


class ParameterRecommender:
    """参数推荐器"""
    
    def __init__(self):
        self.base_configs = {
            DocumentType.CODE: {
                "chunk_size": 512,
                "chunk_overlap": 128,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.7,
                "max_tokens": 2000,
                "splitter_type": "recursive",
                "use_parent_child": False
            },
            DocumentType.TECHNICAL: {
                "chunk_size": 1024,
                "chunk_overlap": 256,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.75,
                "max_tokens": 3000,
                "splitter_type": "recursive",
                "use_parent_child": True
            },
            DocumentType.ACADEMIC: {
                "chunk_size": 2048,
                "chunk_overlap": 512,
                "embedding_model": "text-embedding-3-large",
                "similarity_threshold": 0.8,
                "max_tokens": 4000,
                "splitter_type": "semantic",
                "use_parent_child": True
            },
            DocumentType.NEWS: {
                "chunk_size": 768,
                "chunk_overlap": 192,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.7,
                "max_tokens": 2500,
                "splitter_type": "recursive",
                "use_parent_child": False
            },
            DocumentType.LITERATURE: {
                "chunk_size": 1536,
                "chunk_overlap": 384,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.65,
                "max_tokens": 3500,
                "splitter_type": "recursive",
                "use_parent_child": True
            },
            DocumentType.MARKDOWN: {
                "chunk_size": 1024,
                "chunk_overlap": 256,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.75,
                "max_tokens": 3000,
                "splitter_type": "markdown_header",
                "use_parent_child": True
            },
            DocumentType.MANUAL: {
                "chunk_size": 1024,
                "chunk_overlap": 256,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.75,
                "max_tokens": 3000,
                "splitter_type": "markdown_header",
                "use_parent_child": True
            },
            DocumentType.GENERAL: {
                "chunk_size": 1024,
                "chunk_overlap": 256,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.7,
                "max_tokens": 3000,
                "splitter_type": "recursive",
                "use_parent_child": False
            }
        }
    
    def get_recommendations(
        self,
        document_type: DocumentType,
        content_length: int,
        content: str
    ) -> ParameterRecommendation:
        """获取参数推荐"""
        
        # 获取基础配置
        base_config = self.base_configs[document_type].copy()
        
        # 根据内容长度调整参数
        adjusted_config = self._adjust_by_content_length(base_config, content_length)
        
        # 根据内容特征进一步优化
        optimized_config = self._optimize_by_content_features(adjusted_config, content)
        
        # 设置父子块参数
        if optimized_config.get("use_parent_child", False):
            optimized_config["parent_chunk_size"] = optimized_config["chunk_size"] * 2
            optimized_config["child_chunk_size"] = optimized_config["chunk_size"] // 2
        
        return ParameterRecommendation(
            chunk_size=optimized_config["chunk_size"],
            chunk_overlap=optimized_config["chunk_overlap"],
            embedding_model=optimized_config["embedding_model"],
            similarity_threshold=optimized_config["similarity_threshold"],
            max_tokens=optimized_config["max_tokens"],
            reasoning=self._generate_reasoning(document_type, content_length, optimized_config),
            splitter_type=optimized_config["splitter_type"],
            use_parent_child=optimized_config.get("use_parent_child", False),
            parent_chunk_size=optimized_config.get("parent_chunk_size"),
            child_chunk_size=optimized_config.get("child_chunk_size")
        )
    
    def _adjust_by_content_length(self, config: Dict, content_length: int) -> Dict:
        """根据内容长度调整参数"""
        adjusted = config.copy()
        
        if content_length < 1000:
            # 短文档：减小chunk_size，增加overlap
            adjusted["chunk_size"] = max(256, adjusted["chunk_size"] // 2)
            adjusted["chunk_overlap"] = max(64, adjusted["chunk_overlap"] // 2)
            adjusted["max_tokens"] = max(1000, adjusted["max_tokens"] // 2)
        elif content_length > 10000:
            # 长文档：增加chunk_size，调整overlap
            adjusted["chunk_size"] = min(4096, int(adjusted["chunk_size"] * 1.5))
            adjusted["chunk_overlap"] = min(1024, int(adjusted["chunk_overlap"] * 1.5))
            adjusted["max_tokens"] = min(8000, int(adjusted["max_tokens"] * 1.5))
        
        return adjusted
    
    def _optimize_by_content_features(self, config: Dict, content: str) -> Dict:
        """根据内容特征优化参数"""
        optimized = config.copy()
        
        # 检测代码密度
        code_lines = len([line for line in content.split('\n') 
                         if re.match(r'^\s*(def|class|import|from|if|for|while|try|except)', line)])
        total_lines = len(content.split('\n'))
        code_density = code_lines / total_lines if total_lines > 0 else 0
        
        if code_density > 0.3:
            # 高代码密度：减小chunk_size，增加overlap
            optimized["chunk_size"] = max(256, optimized["chunk_size"] // 2)
            optimized["chunk_overlap"] = min(512, int(optimized["chunk_overlap"] * 1.5))
        
        # 检测段落长度
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        if avg_paragraph_length > 500:
            # 长段落：增加chunk_size
            optimized["chunk_size"] = min(4096, int(optimized["chunk_size"] * 1.2))
        
        # 检测标题密度
        header_count = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        if header_count > 5:
            # 高标题密度：使用markdown分割器
            optimized["splitter_type"] = "markdown_header"
            optimized["use_parent_child"] = True
        
        return optimized
    
    def _generate_reasoning(self, doc_type: DocumentType, content_length: int, config: Dict) -> str:
        """生成推荐理由"""
        reasons = [f"基于文档类型 '{doc_type.value}'"]
        
        if content_length < 1000:
            reasons.append("短文档优化")
        elif content_length > 10000:
            reasons.append("长文档优化")
        
        if config.get("use_parent_child", False):
            reasons.append("启用父子块分割")
        
        if config["splitter_type"] == "markdown_header":
            reasons.append("使用Markdown标题分割")
        elif config["splitter_type"] == "semantic":
            reasons.append("使用语义分割")
        
        return "，".join(reasons)


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.valid_models = [
            "text-embedding-3-small",
            "text-embedding-3-large", 
            "text-embedding-ada-002",
            "bge-m3",
            "gte-large"
        ]
    
    def validate_config(
        self,
        chunk_size: int,
        chunk_overlap: int,
        embedding_model: str,
        similarity_threshold: float,
        max_tokens: int
    ) -> ValidationResult:
        """验证配置参数"""
        errors = []
        warnings = []
        
        # 验证chunk_size
        if chunk_size < 100:
            errors.append("chunk_size 不能小于 100")
        elif chunk_size > 8192:
            errors.append("chunk_size 不能大于 8192")
        elif chunk_size < 256:
            warnings.append("chunk_size 过小可能影响语义完整性")
        elif chunk_size > 4096:
            warnings.append("chunk_size 过大可能影响检索精度")
        
        # 验证chunk_overlap
        if chunk_overlap < 0:
            errors.append("chunk_overlap 不能为负数")
        elif chunk_overlap >= chunk_size:
            errors.append("chunk_overlap 不能大于或等于 chunk_size")
        elif chunk_overlap > chunk_size * 0.5:
            warnings.append("chunk_overlap 过大可能导致重复内容")
        elif chunk_overlap < chunk_size * 0.1:
            warnings.append("chunk_overlap 过小可能导致信息丢失")
        
        # 验证embedding_model
        if embedding_model not in self.valid_models:
            errors.append(f"不支持的embedding模型: {embedding_model}")
        
        # 验证similarity_threshold
        if similarity_threshold < 0 or similarity_threshold > 1:
            errors.append("similarity_threshold 必须在 0-1 之间")
        elif similarity_threshold < 0.5:
            warnings.append("similarity_threshold 过低可能导致不相关结果")
        elif similarity_threshold > 0.9:
            warnings.append("similarity_threshold 过高可能导致结果过少")
        
        # 验证max_tokens
        if max_tokens < 100:
            errors.append("max_tokens 不能小于 100")
        elif max_tokens > 16000:
            errors.append("max_tokens 不能大于 16000")
        elif max_tokens < 1000:
            warnings.append("max_tokens 过小可能限制回答长度")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class ConfigTemplateManager:
    """配置模板管理器"""
    
    def __init__(self):
        self.templates: Dict[str, ConfigTemplate] = {}
    
    async def create_template(self, template_data: ConfigTemplateCreate) -> ConfigTemplate:
        """创建配置模板"""
        template_id = str(uuid.uuid4())
        template = ConfigTemplate(
            id=template_id,
            name=template_data.name,
            description=template_data.description,
            document_type=template_data.document_type,
            config=template_data.config,
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
        self.templates[template_id] = template
        return template
    
    async def get_template(self, template_id: str) -> Optional[ConfigTemplate]:
        """获取配置模板"""
        return self.templates.get(template_id)
    
    async def list_templates(self) -> List[ConfigTemplate]:
        """列出所有模板"""
        return list(self.templates.values())
    
    async def update_template(self, template_id: str, update_data: ConfigTemplateUpdate) -> Optional[ConfigTemplate]:
        """更新配置模板"""
        template = self.templates.get(template_id)
        if not template:
            return None
        
        if update_data.name is not None:
            template.name = update_data.name
        if update_data.description is not None:
            template.description = update_data.description
        if update_data.document_type is not None:
            template.document_type = update_data.document_type
        if update_data.config is not None:
            template.config = update_data.config
        
        template.updated_at = datetime.utcnow().isoformat()
        return template
    
    async def delete_template(self, template_id: str) -> bool:
        """删除配置模板"""
        if template_id in self.templates:
            del self.templates[template_id]
            return True
        return False


class PerformanceAnalyzer:
    """性能分析器"""
    
    def analyze_performance(self, content: str, config: Dict[str, Any]) -> PerformanceMetrics:
        """分析性能指标"""
        chunk_size = config.get("chunk_size", 1024)
        chunk_overlap = config.get("chunk_overlap", 256)
        
        # 估算分块数量
        effective_chunk_size = chunk_size - chunk_overlap
        chunk_count = max(1, len(content) // effective_chunk_size)
        
        # 估算处理时间（毫秒）
        processing_time = len(content) * 0.1 + chunk_count * 50  # 简化估算
        
        # 估算内存使用（MB）
        memory_usage = len(content) / 1024 / 1024 * 2 + chunk_count * 0.1
        
        # 估算存储需求（MB）
        storage_estimate = chunk_count * 0.5  # 每个向量约0.5MB
        
        # 估算向量数量
        vector_count = chunk_count
        
        return PerformanceMetrics(
            processing_time=processing_time / 1000,  # 转换为秒
            memory_usage=memory_usage,
            storage_estimate=storage_estimate,
            vector_count=vector_count,
            chunk_count=chunk_count
        )


class SmartConfigService:
    """智能配置服务"""
    
    def __init__(self):
        self.document_detector = DocumentTypeDetector()
        self.parameter_recommender = ParameterRecommender()
        self.config_validator = ConfigValidator()
        self.template_manager = ConfigTemplateManager()
        self.performance_analyzer = PerformanceAnalyzer()
        self.advanced_preview_service = AdvancedPreviewService()
        self.hybrid_chunker = HybridChunker()
        self.embedding_router = EmbeddingRouter()
    
    async def get_smart_config(
        self,
        request: SmartConfigRequest
    ) -> SmartConfigResponse:
        """获取智能配置推荐"""
        start_time = time.time()
        
        # 检测文档类型
        document_type = self.document_detector.detect_document_type(request.content)
        confidence = self.document_detector.get_confidence_score(request.content, document_type)
        
        # 获取参数推荐
        recommendations = self.parameter_recommender.get_recommendations(
            document_type, len(request.content), request.content
        )
        
        # 性能分析
        performance = self.performance_analyzer.analyze_performance(
            request.content, recommendations.recommended_config
        )
        
        # 高级预览
        preview = await self.advanced_preview_service.get_comprehensive_preview(
            request.content, recommendations.recommended_config
        )
        
        processing_time = time.time() - start_time
        
        return SmartConfigResponse(
            document_type=document_type,
            confidence_score=confidence,
            recommendations=recommendations,
            performance_metrics=performance,
            processing_time=processing_time,
            advanced_preview=preview
        )
    
    async def validate_custom_config(
        self,
        chunk_size: int,
        chunk_overlap: int,
        embedding_model: str,
        similarity_threshold: float,
        max_tokens: int
    ) -> ValidationResult:
        """验证自定义配置参数"""
        return self.config_validator.validate_config(
            chunk_size, chunk_overlap, embedding_model, similarity_threshold, max_tokens
        )
    
    async def create_template(self, template_data: ConfigTemplateCreate) -> ConfigTemplate:
        """创建配置模板"""
        return await self.template_manager.create_template(template_data)
    
    async def get_template(self, template_id: str) -> Optional[ConfigTemplate]:
        """获取配置模板"""
        return await self.template_manager.get_template(template_id)
    
    async def list_templates(self) -> List[ConfigTemplate]:
        """获取配置模板列表"""
        return await self.template_manager.list_templates()
    
    async def update_template(self, template_id: str, update_data: ConfigTemplateUpdate) -> Optional[ConfigTemplate]:
        """更新配置模板"""
        return await self.template_manager.update_template(template_id, update_data)
    
    async def delete_template(self, template_id: str) -> bool:
        """删除配置模板"""
        return await self.template_manager.delete_template(template_id)
    
    async def apply_template(self, template_id: str, content: str) -> SmartConfigResponse:
        """应用配置模板"""
        template = await self.get_template(template_id)
        if not template:
            raise ValueError("配置模板不存在")
        
        # 使用模板配置
        request = SmartConfigRequest(content=content)
        request.advanced_config = AdvancedConfig(**template.config)
        
        return await self.get_smart_config(request)
    
    async def batch_configure(self, batch_request: BatchConfigRequest) -> BatchConfigResponse:
        """批量配置"""
        results = []
        total_time = 0
        
        for i, content in enumerate(batch_request.contents):
            try:
                start_time = time.time()
                
                # 创建请求
                request = SmartConfigRequest(
                    content=content,
                    advanced_config=batch_request.advanced_config
                )
                
                # 获取配置
                response = await self.get_smart_config(request)
                
                processing_time = time.time() - start_time
                total_time += processing_time
                
                results.append({
                    "index": i,
                    "success": True,
                    "response": response,
                    "processing_time": processing_time
                })
                
            except Exception as e:
                logger.error(f"批量配置失败 {i}: {e}")
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e),
                    "processing_time": 0
                })
        
        return BatchConfigResponse(
            total_contents=len(batch_request.contents),
            successful_configs=len([r for r in results if r["success"]]),
            failed_configs=len([r for r in results if not r["success"]]),
            total_processing_time=total_time,
            results=results
        )
    
    async def get_config_preview(self, content: str, config: Dict[str, Any]) -> ConfigPreview:
        """获取配置预览"""
        # 使用高级预览服务
        preview = await self.advanced_preview_service.get_comprehensive_preview(content, config)
        
        # 计算质量分数
        quality_score = self._calculate_quality_score(content, config)
        
        return ConfigPreview(
            chunks=preview["chunks"],
            performance=preview["performance"],
            suggestions=preview["suggestions"],
            hierarchy=preview["hierarchy"],
            statistics=preview["statistics"],
            quality_score=quality_score,
            preview_time=preview["preview_time"]
        )
    
    async def get_advanced_preview(self, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取高级预览"""
        return await self.advanced_preview_service.get_comprehensive_preview(content, config)
    
    async def get_quick_preview(self, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取快速预览"""
        return await self.advanced_preview_service.get_quick_preview(content, config)
    
    async def compare_configs(self, content: str, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """比较不同配置的效果"""
        return await self.advanced_preview_service.compare_configs(content, configs)
    
    async def get_hybrid_chunks(self, content: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取混合分块"""
        chunks = await self.hybrid_chunker.create_hybrid_chunks(
            content,
            parent_chunk_size=config.get("parent_chunk_size", 1024),
            child_chunk_size=config.get("chunk_size", 512),
            child_overlap=config.get("chunk_overlap", 50),
            use_markdown_structure=config.get("use_markdown", True)
        )
        
        return [
            {
                "chunk_id": chunk.chunk_id,
                "content": chunk.content,
                "chunk_type": chunk.chunk_type.value,
                "parent_id": chunk.parent_id,
                "child_ids": chunk.child_ids,
                "metadata": chunk.metadata,
                "level": chunk.level
            }
            for chunk in chunks
        ]
    
    async def get_embedding_info(self, text: str, model: str) -> Dict[str, Any]:
        """获取Embedding信息"""
        from app.services.embedding_router import EmbeddingModel
        
        embedding_model = EmbeddingModel(model)
        model_info = self.embedding_router.get_model_info(embedding_model)
        cost_estimate = self.embedding_router.estimate_cost(text, embedding_model)
        
        return {
            "model_info": model_info,
            "cost_estimate": cost_estimate,
            "text_length": len(text),
            "token_estimate": len(text.split())  # 简单估算
        }
    
    def _calculate_quality_score(self, content: str, config: Dict[str, Any]) -> float:
        """计算质量分数"""
        score = 0.0
        
        # 分块大小评分
        chunk_size = config.get("chunk_size", 512)
        if 256 <= chunk_size <= 1024:
            score += 0.3
        elif 128 <= chunk_size <= 2048:
            score += 0.2
        else:
            score += 0.1
        
        # 重叠度评分
        overlap = config.get("chunk_overlap", 50)
        if 20 <= overlap <= 200:
            score += 0.2
        else:
            score += 0.1
        
        # Embedding模型评分
        model = config.get("embedding_model", "bge-m3")
        if model in ["text-embedding-3-small", "text-embedding-3-large", "bge-m3"]:
            score += 0.3
        else:
            score += 0.2
        
        # 相似度阈值评分
        threshold = config.get("similarity_threshold", 0.7)
        if 0.6 <= threshold <= 0.9:
            score += 0.2
        else:
            score += 0.1
        
        return min(1.0, score) 