from typing import Dict, List, Optional, Tuple
import re
import json
from dataclasses import dataclass
from enum import Enum

from app.schemas.smart_config import (
    DocumentType,
    SmartConfigRequest,
    SmartConfigResponse,
    ParameterRecommendation,
    ValidationResult
)


class DocumentTypeDetector:
    """文档类型检测器"""
    
    @staticmethod
    def detect_document_type(content: str) -> DocumentType:
        """检测文档类型"""
        content_lower = content.lower()
        
        # 检测代码文档
        if any(keyword in content_lower for keyword in [
            'function', 'class', 'def ', 'import ', 'from ', 'return',
            'if __name__', 'try:', 'except:', 'for ', 'while '
        ]):
            return DocumentType.CODE
        
        # 检测技术文档
        if any(keyword in content_lower for keyword in [
            'api', 'endpoint', 'database', 'schema', 'table', 'column',
            'configuration', 'setup', 'installation', 'deployment'
        ]):
            return DocumentType.TECHNICAL
        
        # 检测学术论文
        if any(keyword in content_lower for keyword in [
            'abstract', 'introduction', 'methodology', 'conclusion',
            'references', 'bibliography', 'figure', 'table'
        ]):
            return DocumentType.ACADEMIC
        
        # 检测新闻文章
        if any(keyword in content_lower for keyword in [
            'breaking', 'news', 'report', 'announcement', 'press release',
            'interview', 'exclusive', 'update'
        ]):
            return DocumentType.NEWS
        
        # 检测小说/文学
        if any(keyword in content_lower for keyword in [
            'chapter', 'scene', 'dialogue', 'character', 'plot',
            'narrative', 'story', 'novel'
        ]):
            return DocumentType.LITERATURE
        
        # 默认为一般文档
        return DocumentType.GENERAL


class ParameterRecommender:
    """参数推荐器"""
    
    @staticmethod
    def get_recommendations(
        document_type: DocumentType,
        content_length: int,
        content: str
    ) -> ParameterRecommendation:
        """获取参数推荐"""
        
        # 基础推荐配置
        base_configs = {
            DocumentType.CODE: {
                "chunk_size": 512,
                "chunk_overlap": 128,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.7,
                "max_tokens": 2000
            },
            DocumentType.TECHNICAL: {
                "chunk_size": 1024,
                "chunk_overlap": 256,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.75,
                "max_tokens": 3000
            },
            DocumentType.ACADEMIC: {
                "chunk_size": 2048,
                "chunk_overlap": 512,
                "embedding_model": "text-embedding-3-large",
                "similarity_threshold": 0.8,
                "max_tokens": 4000
            },
            DocumentType.NEWS: {
                "chunk_size": 768,
                "chunk_overlap": 192,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.7,
                "max_tokens": 2500
            },
            DocumentType.LITERATURE: {
                "chunk_size": 1536,
                "chunk_overlap": 384,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.65,
                "max_tokens": 3500
            },
            DocumentType.GENERAL: {
                "chunk_size": 1024,
                "chunk_overlap": 256,
                "embedding_model": "text-embedding-3-small",
                "similarity_threshold": 0.7,
                "max_tokens": 3000
            }
        }
        
        # 获取基础配置
        base_config = base_configs[document_type]
        
        # 根据内容长度调整参数
        adjusted_config = ParameterRecommender._adjust_by_content_length(
            base_config, content_length
        )
        
        # 根据内容特征进一步优化
        optimized_config = ParameterRecommender._optimize_by_content_features(
            adjusted_config, content
        )
        
        return ParameterRecommendation(
            chunk_size=optimized_config["chunk_size"],
            chunk_overlap=optimized_config["chunk_overlap"],
            embedding_model=optimized_config["embedding_model"],
            similarity_threshold=optimized_config["similarity_threshold"],
            max_tokens=optimized_config["max_tokens"],
            reasoning=f"基于文档类型 '{document_type.value}' 和内容长度 {content_length} 字符推荐"
        )
    
    @staticmethod
    def _adjust_by_content_length(
        config: Dict,
        content_length: int
    ) -> Dict:
        """根据内容长度调整参数"""
        adjusted = config.copy()
        
        if content_length < 1000:
            # 短文档：减小chunk_size，增加overlap
            adjusted["chunk_size"] = max(256, adjusted["chunk_size"] // 2)
            adjusted["chunk_overlap"] = max(64, adjusted["chunk_overlap"] // 2)
            adjusted["max_tokens"] = max(1000, adjusted["max_tokens"] // 2)
        elif content_length > 10000:
            # 长文档：增加chunk_size，调整overlap
            adjusted["chunk_size"] = min(4096, adjusted["chunk_size"] * 1.5)
            adjusted["chunk_overlap"] = min(1024, adjusted["chunk_overlap"] * 1.5)
            adjusted["max_tokens"] = min(8000, adjusted["max_tokens"] * 1.5)
        
        return adjusted
    
    @staticmethod
    def _optimize_by_content_features(
        config: Dict,
        content: str
    ) -> Dict:
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
            optimized["chunk_overlap"] = min(512, optimized["chunk_overlap"] * 1.5)
        
        # 检测段落长度
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        if avg_paragraph_length > 500:
            # 长段落：增加chunk_size
            optimized["chunk_size"] = min(4096, optimized["chunk_size"] * 1.2)
        
        return optimized


class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_config(
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
        
        # 验证chunk_overlap
        if chunk_overlap < 0:
            errors.append("chunk_overlap 不能为负数")
        elif chunk_overlap >= chunk_size:
            errors.append("chunk_overlap 不能大于或等于 chunk_size")
        elif chunk_overlap > chunk_size * 0.5:
            warnings.append("chunk_overlap 过大可能导致重复内容")
        
        # 验证embedding_model
        valid_models = [
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002"
        ]
        if embedding_model not in valid_models:
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
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )


class SmartConfigService:
    """智能配置服务"""
    
    def __init__(self):
        self.detector = DocumentTypeDetector()
        self.recommender = ParameterRecommender()
        self.validator = ConfigValidator()
    
    async def get_smart_config(
        self,
        request: SmartConfigRequest
    ) -> SmartConfigResponse:
        """获取智能配置"""
        
        # 检测文档类型
        document_type = self.detector.detect_document_type(request.content)
        
        # 计算内容长度
        content_length = len(request.content)
        
        # 获取参数推荐
        recommendation = self.recommender.get_recommendations(
            document_type, content_length, request.content
        )
        
        # 验证推荐参数
        validation = self.validator.validate_config(
            recommendation.chunk_size,
            recommendation.chunk_overlap,
            recommendation.embedding_model,
            recommendation.similarity_threshold,
            recommendation.max_tokens
        )
        
        return SmartConfigResponse(
            document_type=document_type,
            content_length=content_length,
            recommendation=recommendation,
            validation=validation
        )
    
    async def validate_custom_config(
        self,
        chunk_size: int,
        chunk_overlap: int,
        embedding_model: str,
        similarity_threshold: float,
        max_tokens: int
    ) -> ValidationResult:
        """验证自定义配置"""
        return self.validator.validate_config(
            chunk_size, chunk_overlap, embedding_model,
            similarity_threshold, max_tokens
        ) 