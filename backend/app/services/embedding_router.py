"""
Embedding路由服务
支持多模型选择和父子联合Embedding
"""
import asyncio
import aiohttp
import numpy as np
from typing import List, Optional, Dict, Any
import logging
from enum import Enum

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingModel(str, Enum):
    """支持的Embedding模型"""
    OPENAI_ADA_002 = "text-embedding-ada-002"
    OPENAI_3_SMALL = "text-embedding-3-small"
    OPENAI_3_LARGE = "text-embedding-3-large"
    BGE_M3 = "bge-m3"
    GTE_LARGE = "gte-large"
    MINILM = "minilm"


class TextType(str, Enum):
    """文本类型"""
    SHORT = "short"  # 短文本/问句
    LONG = "long"    # 长文本/文档
    CODE = "code"    # 代码
    HYBRID = "hybrid"  # 父子联合


class EmbeddingRouter:
    """Embedding路由服务"""
    
    def __init__(self):
        self.model_configs = {
            EmbeddingModel.OPENAI_ADA_002: {
                "url": f"{settings.OPENAI_BASE_URL}/embeddings",
                "headers": {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                "dimension": 1536,
                "max_tokens": 8191,
                "cost_per_1k": 0.0001
            },
            EmbeddingModel.OPENAI_3_SMALL: {
                "url": f"{settings.OPENAI_BASE_URL}/embeddings",
                "headers": {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                "dimension": 1536,
                "max_tokens": 8191,
                "cost_per_1k": 0.00002
            },
            EmbeddingModel.OPENAI_3_LARGE: {
                "url": f"{settings.OPENAI_BASE_URL}/embeddings",
                "headers": {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                "dimension": 3072,
                "max_tokens": 8191,
                "cost_per_1k": 0.00013
            },
            EmbeddingModel.BGE_M3: {
                "url": "http://localhost:8001/embeddings",  # 本地模型服务
                "headers": {"Content-Type": "application/json"},
                "dimension": 1024,
                "max_tokens": 8192,
                "cost_per_1k": 0.0  # 本地模型无成本
            },
            EmbeddingModel.GTE_LARGE: {
                "url": "http://localhost:8002/embeddings",  # 本地模型服务
                "headers": {"Content-Type": "application/json"},
                "dimension": 1024,
                "max_tokens": 8192,
                "cost_per_1k": 0.0
            },
            EmbeddingModel.MINILM: {
                "url": "http://localhost:8003/embeddings",  # 本地模型服务
                "headers": {"Content-Type": "application/json"},
                "dimension": 384,
                "max_tokens": 512,
                "cost_per_1k": 0.0
            }
        }
        
        # 路由策略
        self.routing_strategy = {
            TextType.SHORT: [EmbeddingModel.OPENAI_3_SMALL, EmbeddingModel.OPENAI_ADA_002],
            TextType.LONG: [EmbeddingModel.BGE_M3, EmbeddingModel.GTE_LARGE],
            TextType.CODE: [EmbeddingModel.MINILM, EmbeddingModel.OPENAI_3_SMALL],
            TextType.HYBRID: [EmbeddingModel.BGE_M3, EmbeddingModel.GTE_LARGE]
        }
    
    def select_model(self, text: str, text_type: Optional[TextType] = None, 
                    preferred_model: Optional[str] = None) -> EmbeddingModel:
        """选择Embedding模型"""
        if preferred_model and preferred_model in [m.value for m in EmbeddingModel]:
            return EmbeddingModel(preferred_model)
        
        # 自动检测文本类型
        if not text_type:
            text_type = self._detect_text_type(text)
        
        # 根据文本类型选择模型
        available_models = self.routing_strategy.get(text_type, [EmbeddingModel.OPENAI_3_SMALL])
        
        # 优先选择本地模型（降低成本）
        for model in available_models:
            if self._is_model_available(model):
                return model
        
        # 降级到OpenAI
        return EmbeddingModel.OPENAI_3_SMALL
    
    def _detect_text_type(self, text: str) -> TextType:
        """检测文本类型"""
        text_length = len(text)
        
        if text_length < 100:
            return TextType.SHORT
        elif text_length > 1000:
            return TextType.LONG
        elif self._is_code_text(text):
            return TextType.CODE
        else:
            return TextType.SHORT
    
    def _is_code_text(self, text: str) -> bool:
        """检测是否为代码文本"""
        code_indicators = [
            'def ', 'class ', 'import ', 'from ', 'return ',
            'function ', 'const ', 'let ', 'var ', 'public ',
            'private ', 'if ', 'for ', 'while ', 'try:'
        ]
        return any(indicator in text for indicator in code_indicators)
    
    def _is_model_available(self, model: EmbeddingModel) -> bool:
        """检查模型是否可用"""
        # 这里应该实现模型可用性检查
        # 暂时简单判断：本地模型总是可用，OpenAI需要API key
        if model in [EmbeddingModel.BGE_M3, EmbeddingModel.GTE_LARGE, EmbeddingModel.MINILM]:
            return True
        elif model in [EmbeddingModel.OPENAI_ADA_002, EmbeddingModel.OPENAI_3_SMALL, EmbeddingModel.OPENAI_3_LARGE]:
            return bool(settings.OPENAI_API_KEY)
        return False
    
    async def get_embedding(self, text: str, model: Optional[EmbeddingModel] = None,
                          text_type: Optional[TextType] = None) -> List[float]:
        """获取文本向量"""
        if not model:
            model = self.select_model(text, text_type)
        
        config = self.model_configs[model]
        
        try:
            if model in [EmbeddingModel.OPENAI_ADA_002, EmbeddingModel.OPENAI_3_SMALL, EmbeddingModel.OPENAI_3_LARGE]:
                return await self._get_openai_embedding(text, model, config)
            else:
                return await self._get_local_embedding(text, model, config)
        except Exception as e:
            logger.error(f"Embedding获取失败: {e}")
            # 降级到简单向量化
            return self._fallback_embedding(text, config["dimension"])
    
    async def _get_openai_embedding(self, text: str, model: EmbeddingModel, 
                                  config: Dict[str, Any]) -> List[float]:
        """获取OpenAI Embedding"""
        async with aiohttp.ClientSession() as session:
            data = {
                "input": text,
                "model": model.value
            }
            
            async with session.post(
                config["url"],
                headers=config["headers"],
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["data"][0]["embedding"]
                else:
                    raise Exception(f"OpenAI API错误: {response.status}")
    
    async def _get_local_embedding(self, text: str, model: EmbeddingModel,
                                 config: Dict[str, Any]) -> List[float]:
        """获取本地模型Embedding"""
        async with aiohttp.ClientSession() as session:
            data = {
                "text": text,
                "model": model.value
            }
            
            async with session.post(
                config["url"],
                headers=config["headers"],
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["embedding"]
                else:
                    raise Exception(f"本地模型API错误: {response.status}")
    
    def _fallback_embedding(self, text: str, dimension: int) -> List[float]:
        """降级向量化"""
        import string
        import random
        
        # 简单的字符频率向量化
        vector = [0.0] * dimension
        
        # 字符频率
        for char in text.lower():
            if char in string.ascii_lowercase:
                idx = (ord(char) - ord('a')) % dimension
                vector[idx] += 1.0
        
        # 归一化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = [v / norm for v in vector]
        
        return vector
    
    async def get_hybrid_embedding(self, parent_text: str, child_text: str,
                                 parent_weight: float = 0.3, child_weight: float = 0.7,
                                 model: Optional[EmbeddingModel] = None) -> List[float]:
        """获取父子联合Embedding"""
        # 选择适合长文本的模型
        if not model:
            model = self.select_model(parent_text + child_text, TextType.HYBRID)
        
        # 分别获取父文本和子文本的向量
        parent_embedding = await self.get_embedding(parent_text, model)
        child_embedding = await self.get_embedding(child_text, model)
        
        # 确保向量维度一致
        if len(parent_embedding) != len(child_embedding):
            # 如果维度不同，使用较小的维度
            min_dim = min(len(parent_embedding), len(child_embedding))
            parent_embedding = parent_embedding[:min_dim]
            child_embedding = child_embedding[:min_dim]
        
        # 加权组合
        hybrid_embedding = [
            parent_weight * p + child_weight * c
            for p, c in zip(parent_embedding, child_embedding)
        ]
        
        # 归一化
        norm = np.linalg.norm(hybrid_embedding)
        if norm > 0:
            hybrid_embedding = [v / norm for v in hybrid_embedding]
        
        return hybrid_embedding
    
    def get_model_info(self, model: EmbeddingModel) -> Dict[str, Any]:
        """获取模型信息"""
        config = self.model_configs[model]
        return {
            "model": model.value,
            "dimension": config["dimension"],
            "max_tokens": config["max_tokens"],
            "cost_per_1k": config["cost_per_1k"],
            "available": self._is_model_available(model)
        }
    
    def estimate_cost(self, text: str, model: EmbeddingModel) -> float:
        """估算成本"""
        config = self.model_configs[model]
        token_count = len(text.split())  # 简单估算
        return (token_count / 1000) * config["cost_per_1k"]
    
    async def batch_embedding(self, texts: List[str], model: Optional[EmbeddingModel] = None) -> List[List[float]]:
        """批量获取向量"""
        if not model:
            # 使用第一个文本选择模型
            model = self.select_model(texts[0] if texts else "")
        
        # 并发获取向量
        tasks = [self.get_embedding(text, model) for text in texts]
        embeddings = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常
        result = []
        for i, embedding in enumerate(embeddings):
            if isinstance(embedding, Exception):
                logger.error(f"文本 {i} 向量化失败: {embedding}")
                # 使用降级向量化
                config = self.model_configs[model]
                result.append(self._fallback_embedding(texts[i], config["dimension"]))
            else:
                result.append(embedding)
        
        return result 