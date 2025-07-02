"""
轻量级聊天服务
简化功能，降低资源消耗
"""

import asyncio
import logging
import time
import gc
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import json

from app.core.lightweight_config import lightweight_config
from app.services.model_service import ModelService
from app.utils.text_processor import TextProcessor

logger = logging.getLogger(__name__)


class LightweightChatService:
    """轻量级聊天服务"""
    
    def __init__(self):
        self.config = lightweight_config.get_optimization_config()
        self.model_service = ModelService()
        self.text_processor = TextProcessor()
        
        # 资源限制
        self.max_concurrent = self.config["max_concurrent"]
        self.max_memory = self.config["max_memory"]
        
        # 内存优化
        self.enable_memory_optimization = self.config["memory_optimization"]
        self.cleanup_interval = self.config["cleanup_interval"]
        
        # 活跃请求计数
        self.active_requests = 0
        self.request_semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # 简化缓存
        self.response_cache = {}
        self.cache_ttl = lightweight_config.CACHE_TTL
        self.max_cache_size = lightweight_config.MAX_CACHE_SIZE
        
        # 启动清理任务
        if self.enable_memory_optimization:
            asyncio.create_task(self._cleanup_task())
    
    async def chat(
        self,
        user_id: int,
        message: str,
        knowledge_base_id: Optional[int] = None,
        conversation_id: Optional[str] = None,
        model_name: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """聊天接口"""
        try:
            # 检查资源限制
            if not await self._check_resource_limits():
                return {
                    "success": False,
                    "message": "系统资源不足，请稍后重试",
                    "data": None
                }
            
            # 获取模型配置
            model_config = await self._get_model_config(model_name)
            if not model_config:
                return {
                    "success": False,
                    "message": "模型配置无效",
                    "data": None
                }
            
            # 检查缓存
            cache_key = self._generate_cache_key(user_id, message, knowledge_base_id, model_name)
            if not stream and cache_key in self.response_cache:
                cached_response = self.response_cache[cache_key]
                if time.time() - cached_response["timestamp"] < self.cache_ttl:
                    return {
                        "success": True,
                        "message": "成功",
                        "data": cached_response["response"]
                    }
            
            # 构建简化上下文
            context = await self._build_simple_context(user_id, message, knowledge_base_id, conversation_id)
            
            # 生成响应
            if stream:
                return await self._stream_chat(context, model_config)
            else:
                return await self._normal_chat(context, model_config, cache_key)
                
        except Exception as e:
            logger.error(f"聊天服务错误: {e}")
            return {
                "success": False,
                "message": f"聊天服务错误: {str(e)}",
                "data": None
            }
        finally:
            # 减少活跃请求计数
            self.active_requests = max(0, self.active_requests - 1)
    
    async def _check_resource_limits(self) -> bool:
        """检查资源限制"""
        # 检查并发限制
        if self.active_requests >= self.max_concurrent:
            logger.warning(f"达到最大并发限制: {self.max_concurrent}")
            return False
        
        # 检查内存使用
        if self.enable_memory_optimization:
            current_memory = self._get_memory_usage()
            if current_memory > self.max_memory:
                logger.warning(f"内存使用超限: {current_memory}MB > {self.max_memory}MB")
                await self._force_cleanup()
                return False
        
        return True
    
    def _get_memory_usage(self) -> float:
        """获取内存使用量（简化版）"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.used / (1024 * 1024)  # MB
        except:
            return 0.0
    
    async def _get_model_config(self, model_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """获取模型配置"""
        try:
            if model_name:
                return await self.model_service.get_model_config(model_name)
            else:
                # 使用默认模型
                default_model = lightweight_config.DEFAULT_MODEL
                return await self.model_service.get_model_config(default_model)
        except Exception as e:
            logger.error(f"获取模型配置失败: {e}")
            return None
    
    async def _build_simple_context(
        self,
        user_id: int,
        message: str,
        knowledge_base_id: Optional[int],
        conversation_id: Optional[str]
    ) -> Dict[str, Any]:
        """构建简化聊天上下文"""
        context = {
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now(),
            "conversation_id": conversation_id or f"conv_{user_id}_{int(time.time())}"
        }
        
        # 简化知识库上下文
        if knowledge_base_id:
            kb_context = await self._get_simple_kb_context(knowledge_base_id, message)
            context["knowledge_base"] = kb_context
        
        # 简化对话历史（只保留最近3条）
        if conversation_id:
            history = await self._get_simple_history(conversation_id)
            context["history"] = history[-3:] if history else []
        
        return context
    
    async def _get_simple_kb_context(self, kb_id: int, query: str) -> Dict[str, Any]:
        """获取简化知识库上下文"""
        try:
            # 简化检索，只返回少量结果
            max_results = lightweight_config.MAX_SEARCH_RESULTS
            
            # 这里应该调用轻量级向量服务
            # 暂时返回空结果
            return {
                "knowledge_base_id": kb_id,
                "relevant_docs": [],
                "search_time": 0.05
            }
        except Exception as e:
            logger.error(f"获取知识库上下文失败: {e}")
            return {}
    
    async def _get_simple_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """获取简化对话历史"""
        try:
            # 这里应该从数据库获取对话历史
            # 暂时返回空历史
            return []
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    async def _normal_chat(
        self,
        context: Dict[str, Any],
        model_config: Dict[str, Any],
        cache_key: str
    ) -> Dict[str, Any]:
        """普通聊天（非流式）"""
        async with self.request_semaphore:
            self.active_requests += 1
            
            try:
                # 构建简化提示词
                prompt = self._build_simple_prompt(context)
                
                # 调用模型
                response = await self._call_model(prompt, model_config)
                
                # 缓存响应
                self._cache_response(cache_key, response)
                
                return {
                    "success": True,
                    "message": "成功",
                    "data": {
                        "response": response,
                        "conversation_id": context["conversation_id"],
                        "model": model_config["name"],
                        "usage": {
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": len(response.split()),
                            "total_tokens": len(prompt.split()) + len(response.split())
                        }
                    }
                }
                
            except asyncio.TimeoutError:
                logger.error("模型调用超时")
                return {
                    "success": False,
                    "message": "响应超时，请稍后重试",
                    "data": None
                }
            except Exception as e:
                logger.error(f"模型调用失败: {e}")
                return {
                    "success": False,
                    "message": f"模型调用失败: {str(e)}",
                    "data": None
                }
    
    async def _stream_chat(
        self,
        context: Dict[str, Any],
        model_config: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        async with self.request_semaphore:
            self.active_requests += 1
            
            try:
                # 构建简化提示词
                prompt = self._build_simple_prompt(context)
                
                # 流式调用模型
                async for chunk in self._stream_call_model(prompt, model_config):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"流式聊天失败: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
            finally:
                self.active_requests = max(0, self.active_requests - 1)
    
    def _build_simple_prompt(self, context: Dict[str, Any]) -> str:
        """构建简化提示词"""
        prompt_parts = []
        
        # 系统提示词
        system_prompt = "你是一个智能助手，请简洁准确地回答用户问题。"
        prompt_parts.append(f"系统: {system_prompt}")
        
        # 简化知识库上下文
        if "knowledge_base" in context and context["knowledge_base"].get("relevant_docs"):
            kb_context = "参考信息：\n"
            for doc in context["knowledge_base"]["relevant_docs"][:3]:  # 只取前3条
                kb_context += f"- {doc['content'][:200]}...\n"  # 限制长度
            prompt_parts.append(f"参考: {kb_context}")
        
        # 简化对话历史
        if "history" in context and context["history"]:
            history_context = "对话历史：\n"
            for msg in context["history"]:
                history_context += f"{msg['role']}: {msg['content'][:100]}...\n"  # 限制长度
            prompt_parts.append(f"历史: {history_context}")
        
        # 用户消息
        prompt_parts.append(f"用户: {context['message']}")
        prompt_parts.append("助手: ")
        
        return "\n".join(prompt_parts)
    
    async def _call_model(self, prompt: str, model_config: Dict[str, Any]) -> str:
        """调用模型"""
        try:
            # 使用模型服务调用
            response = await self.model_service.generate_text(
                prompt=prompt,
                model_name=model_config["name"],
                max_tokens=min(model_config.get("max_tokens", 500), 500),  # 限制token数
                temperature=model_config.get("temperature", 0.7),
                timeout=lightweight_config.API_TIMEOUT
            )
            return response
        except Exception as e:
            logger.error(f"模型调用失败: {e}")
            raise
    
    async def _stream_call_model(
        self,
        prompt: str,
        model_config: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """流式调用模型"""
        try:
            async for chunk in self.model_service.generate_text_stream(
                prompt=prompt,
                model_name=model_config["name"],
                max_tokens=min(model_config.get("max_tokens", 500), 500),  # 限制token数
                temperature=model_config.get("temperature", 0.7),
                timeout=lightweight_config.API_TIMEOUT
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            logger.error(f"流式模型调用失败: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    def _generate_cache_key(
        self,
        user_id: int,
        message: str,
        knowledge_base_id: Optional[int],
        model_name: Optional[str]
    ) -> str:
        """生成缓存键"""
        key_parts = [
            str(user_id),
            message[:50],  # 限制消息长度
            str(knowledge_base_id or ""),
            model_name or "default"
        ]
        return "_".join(key_parts)
    
    def _cache_response(self, cache_key: str, response: str):
        """缓存响应"""
        try:
            self.response_cache[cache_key] = {
                "response": response,
                "timestamp": time.time()
            }
            
            # 限制缓存大小
            if len(self.response_cache) > self.max_cache_size:
                # 删除最旧的缓存
                oldest_key = min(self.response_cache.keys(), 
                               key=lambda k: self.response_cache[k]["timestamp"])
                del self.response_cache[oldest_key]
                
        except Exception as e:
            logger.error(f"缓存响应失败: {e}")
    
    async def _force_cleanup(self):
        """强制清理"""
        try:
            # 清理缓存
            current_time = time.time()
            expired_keys = [
                key for key, value in self.response_cache.items()
                if current_time - value["timestamp"] > self.cache_ttl
            ]
            for key in expired_keys:
                del self.response_cache[key]
            
            # 强制垃圾回收
            gc.collect()
            
            logger.info("强制清理完成")
        except Exception as e:
            logger.error(f"强制清理失败: {e}")
    
    async def _cleanup_task(self):
        """定期清理任务"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._force_cleanup()
            except Exception as e:
                logger.error(f"清理任务失败: {e}")
    
    async def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "service": "lightweight_chat",
            "active_requests": self.active_requests,
            "max_concurrent": self.max_concurrent,
            "memory_usage": self._get_memory_usage(),
            "max_memory": self.max_memory,
            "cache_size": len(self.response_cache),
            "memory_optimization": self.enable_memory_optimization
        }


# 全局实例
lightweight_chat_service = LightweightChatService() 