"""
轻量级图片向量化服务
使用CLIP模型进行图片向量化，支持轻量级部署
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import numpy as np
from PIL import Image
import io
import base64

from app.core.lightweight_config import lightweight_config
from app.utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class LightweightImageService:
    """轻量级图片向量化服务"""
    
    def __init__(self):
        self.config = lightweight_config.get_image_config()
        self.text_processor = TextProcessor()
        
        # 初始化CLIP模型
        self._init_clip_model()
        
        # 图片缓存
        self.image_cache = {}
        self.max_cache_size = 100
    
    def _init_clip_model(self):
        """初始化CLIP模型"""
        try:
            import clip
            import torch
            
            # 加载CLIP模型
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)
            
            logger.info(f"CLIP模型加载成功，设备: {self.device}")
            
        except ImportError:
            logger.error("CLIP未安装，请运行: pip install clip")
            self.model = None
            self.preprocess = None
        except Exception as e:
            logger.error(f"CLIP模型加载失败: {e}")
            self.model = None
            self.preprocess = None
    
    async def vectorize_image(self, image_data: Union[bytes, str, Image.Image]) -> Optional[List[float]]:
        """向量化图片"""
        try:
            if not self.model:
                logger.error("CLIP模型未加载")
                return None
            
            # 处理图片数据
            image = await self._process_image(image_data)
            if image is None:
                return None
            
            # 生成向量
            vector = await self._generate_image_vector(image)
            
            return vector
            
        except Exception as e:
            logger.error(f"图片向量化失败: {e}")
            return None
    
    async def vectorize_images_batch(self, image_data_list: List[Union[bytes, str, Image.Image]]) -> List[Optional[List[float]]]:
        """批量向量化图片"""
        try:
            if not self.model:
                logger.error("CLIP模型未加载")
                return [None] * len(image_data_list)
            
            vectors = []
            for image_data in image_data_list:
                vector = await self.vectorize_image(image_data)
                vectors.append(vector)
            
            return vectors
            
        except Exception as e:
            logger.error(f"批量图片向量化失败: {e}")
            return [None] * len(image_data_list)
    
    async def _process_image(self, image_data: Union[bytes, str, Image.Image]) -> Optional[Image.Image]:
        """处理图片数据"""
        try:
            if isinstance(image_data, Image.Image):
                image = image_data
            elif isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                # 处理base64或文件路径
                if image_data.startswith('data:image'):
                    # base64数据
                    image_data = image_data.split(',')[1]
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                elif os.path.exists(image_data):
                    # 文件路径
                    image = Image.open(image_data)
                else:
                    logger.error(f"无效的图片数据: {type(image_data)}")
                    return None
            else:
                logger.error(f"不支持的图片数据类型: {type(image_data)}")
                return None
            
            # 转换为RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 调整图片大小
            max_size = self.config["image_max_size"]
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"处理图片失败: {e}")
            return None
    
    async def _generate_image_vector(self, image: Image.Image) -> Optional[List[float]]:
        """生成图片向量"""
        try:
            import torch
            
            # 预处理图片
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # 生成向量
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                vector = image_features.cpu().numpy()[0].tolist()
            
            return vector
            
        except Exception as e:
            logger.error(f"生成图片向量失败: {e}")
            return None
    
    async def search_similar_images(
        self, 
        query_image: Union[bytes, str, Image.Image], 
        image_vectors: List[Dict[str, Any]], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """搜索相似图片"""
        try:
            # 向量化查询图片
            query_vector = await self.vectorize_image(query_image)
            if query_vector is None:
                return []
            
            # 计算相似度
            similarities = []
            for img_data in image_vectors:
                if "vector" in img_data:
                    similarity = self._calculate_similarity(query_vector, img_data["vector"])
                    similarities.append({
                        "id": img_data.get("id"),
                        "similarity": similarity,
                        "metadata": img_data.get("metadata", {}),
                        "image_path": img_data.get("image_path", "")
                    })
            
            # 排序并返回top_k结果
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"搜索相似图片失败: {e}")
            return []
    
    def _calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """计算向量相似度"""
        try:
            # 使用余弦相似度
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"计算相似度失败: {e}")
            return 0.0
    
    async def extract_image_text(self, image_data: Union[bytes, str, Image.Image]) -> Optional[str]:
        """提取图片中的文本"""
        try:
            # 这里可以集成OCR功能
            # 暂时返回空字符串
            return ""
            
        except Exception as e:
            logger.error(f"提取图片文本失败: {e}")
            return None
    
    async def generate_image_description(self, image_data: Union[bytes, str, Image.Image]) -> Optional[str]:
        """生成图片描述"""
        try:
            if not self.model:
                return None
            
            import torch
            
            # 处理图片
            image = await self._process_image(image_data)
            if image is None:
                return None
            
            # 预定义一些描述模板
            templates = [
                "a photo of {}",
                "an image showing {}",
                "a picture of {}",
                "a photograph of {}"
            ]
            
            # 使用CLIP进行零样本分类
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # 简单的物体类别
            classes = ["person", "animal", "building", "vehicle", "food", "nature", "object"]
            
            with torch.no_grad():
                image_features = self.model.encode_image(image_tensor)
                
                # 计算与每个类别的相似度
                similarities = []
                for template in templates:
                    for class_name in classes:
                        text = template.format(class_name)
                        text_tokens = clip.tokenize([text]).to(self.device)
                        text_features = self.model.encode_text(text_tokens)
                        
                        similarity = torch.cosine_similarity(image_features, text_features)
                        similarities.append((similarity.item(), class_name))
                
                # 找到最相似的类别
                best_similarity, best_class = max(similarities)
                
                # 生成描述
                if best_similarity > 0.3:  # 相似度阈值
                    return f"This image shows {best_class}."
                else:
                    return "This is an image."
            
        except Exception as e:
            logger.error(f"生成图片描述失败: {e}")
            return None
    
    async def get_image_metadata(self, image_data: Union[bytes, str, Image.Image]) -> Dict[str, Any]:
        """获取图片元数据"""
        try:
            image = await self._process_image(image_data)
            if image is None:
                return {}
            
            metadata = {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "aspect_ratio": image.width / image.height if image.height > 0 else 0,
                "processed_at": datetime.now().isoformat()
            }
            
            # 生成描述
            description = await self.generate_image_description(image_data)
            if description:
                metadata["description"] = description
            
            return metadata
            
        except Exception as e:
            logger.error(f"获取图片元数据失败: {e}")
            return {}
    
    def _cache_image_vector(self, image_id: str, vector: List[float]):
        """缓存图片向量"""
        try:
            self.image_cache[image_id] = {
                "vector": vector,
                "timestamp": datetime.now().timestamp()
            }
            
            # 限制缓存大小
            if len(self.image_cache) > self.max_cache_size:
                # 删除最旧的缓存
                oldest_key = min(self.image_cache.keys(), 
                               key=lambda k: self.image_cache[k]["timestamp"])
                del self.image_cache[oldest_key]
                
        except Exception as e:
            logger.error(f"缓存图片向量失败: {e}")
    
    async def clear_cache(self):
        """清理缓存"""
        try:
            self.image_cache.clear()
            logger.info("图片服务缓存已清理")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        try:
            return {
                "service": "lightweight_image",
                "status": "running" if self.model else "error",
                "model_loaded": self.model is not None,
                "device": getattr(self, 'device', 'unknown'),
                "cache_size": len(self.image_cache),
                "max_cache_size": self.max_cache_size,
                "enable_image_vectorization": self.config["enable_image_vectorization"]
            }
        except Exception as e:
            logger.error(f"获取服务状态失败: {e}")
            return {"status": "error", "error": str(e)}


# 全局实例
lightweight_image_service = LightweightImageService() 