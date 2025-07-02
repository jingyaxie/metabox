"""
轻量级缓存服务
使用内存缓存替代Redis，降低资源消耗
"""

import time
import logging
import threading
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import json

from app.core.lightweight_config import lightweight_config

logger = logging.getLogger(__name__)


class LightweightCacheService:
    """轻量级缓存服务"""
    
    def __init__(self):
        self.config = lightweight_config.get_cache_config()
        self.cache = {}
        self.cache_ttl = self.config["ttl"]
        self.max_size = self.config["max_size"]
        
        # 线程锁
        self.lock = threading.Lock()
        
        # 统计信息
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        
        # 启动清理任务
        self._start_cleanup_task()
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存"""
        try:
            with self.lock:
                # 检查缓存大小
                if len(self.cache) >= self.max_size:
                    self._evict_oldest()
                
                # 设置缓存
                expire_time = time.time() + (ttl or self.cache_ttl)
                self.cache[key] = {
                    "value": value,
                    "expire_time": expire_time,
                    "created_at": time.time()
                }
                
                self.stats["sets"] += 1
                logger.debug(f"缓存设置成功: {key}")
                return True
                
        except Exception as e:
            logger.error(f"设置缓存失败: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        try:
            with self.lock:
                if key not in self.cache:
                    self.stats["misses"] += 1
                    return None
                
                cache_item = self.cache[key]
                
                # 检查是否过期
                if time.time() > cache_item["expire_time"]:
                    del self.cache[key]
                    self.stats["misses"] += 1
                    return None
                
                self.stats["hits"] += 1
                logger.debug(f"缓存命中: {key}")
                return cache_item["value"]
                
        except Exception as e:
            logger.error(f"获取缓存失败: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            with self.lock:
                if key in self.cache:
                    del self.cache[key]
                    self.stats["deletes"] += 1
                    logger.debug(f"缓存删除成功: {key}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"删除缓存失败: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """检查缓存是否存在"""
        try:
            with self.lock:
                if key not in self.cache:
                    return False
                
                cache_item = self.cache[key]
                
                # 检查是否过期
                if time.time() > cache_item["expire_time"]:
                    del self.cache[key]
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"检查缓存存在失败: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """设置缓存过期时间"""
        try:
            with self.lock:
                if key in self.cache:
                    self.cache[key]["expire_time"] = time.time() + ttl
                    logger.debug(f"设置缓存过期时间: {key}, ttl: {ttl}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"设置缓存过期时间失败: {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """获取缓存剩余时间"""
        try:
            with self.lock:
                if key not in self.cache:
                    return -2  # 不存在
                
                cache_item = self.cache[key]
                remaining = cache_item["expire_time"] - time.time()
                
                if remaining <= 0:
                    del self.cache[key]
                    return -2  # 已过期
                
                return int(remaining)
                
        except Exception as e:
            logger.error(f"获取缓存剩余时间失败: {e}")
            return -1  # 错误
    
    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的键"""
        try:
            with self.lock:
                import fnmatch
                keys = []
                
                for key in self.cache.keys():
                    # 检查是否过期
                    cache_item = self.cache[key]
                    if time.time() > cache_item["expire_time"]:
                        del self.cache[key]
                        continue
                    
                    # 匹配模式
                    if fnmatch.fnmatch(key, pattern):
                        keys.append(key)
                
                return keys
                
        except Exception as e:
            logger.error(f"获取缓存键失败: {e}")
            return []
    
    def clear(self) -> bool:
        """清空缓存"""
        try:
            with self.lock:
                self.cache.clear()
                logger.info("缓存已清空")
                return True
                
        except Exception as e:
            logger.error(f"清空缓存失败: {e}")
            return False
    
    def size(self) -> int:
        """获取缓存大小"""
        try:
            with self.lock:
                return len(self.cache)
        except Exception as e:
            logger.error(f"获取缓存大小失败: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            with self.lock:
                total_requests = self.stats["hits"] + self.stats["misses"]
                hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
                
                return {
                    "size": len(self.cache),
                    "max_size": self.max_size,
                    "hits": self.stats["hits"],
                    "misses": self.stats["misses"],
                    "sets": self.stats["sets"],
                    "deletes": self.stats["deletes"],
                    "hit_rate": hit_rate,
                    "total_requests": total_requests
                }
                
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def _evict_oldest(self):
        """淘汰最旧的缓存"""
        try:
            if not self.cache:
                return
            
            # 找到最旧的缓存项
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]["created_at"])
            
            # 删除最旧的缓存
            del self.cache[oldest_key]
            logger.debug(f"淘汰最旧缓存: {oldest_key}")
            
        except Exception as e:
            logger.error(f"淘汰最旧缓存失败: {e}")
    
    def _cleanup_expired(self):
        """清理过期缓存"""
        try:
            with self.lock:
                current_time = time.time()
                expired_keys = []
                
                for key, item in self.cache.items():
                    if current_time > item["expire_time"]:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache[key]
                
                if expired_keys:
                    logger.debug(f"清理了 {len(expired_keys)} 个过期缓存")
                    
        except Exception as e:
            logger.error(f"清理过期缓存失败: {e}")
    
    def _start_cleanup_task(self):
        """启动清理任务"""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(60)  # 每分钟清理一次
                    self._cleanup_expired()
                except Exception as e:
                    logger.error(f"清理任务失败: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("缓存清理任务已启动")
    
    # 兼容Redis接口的方法
    def setex(self, key: str, ttl: int, value: Any) -> bool:
        """设置缓存并指定过期时间"""
        return self.set(key, value, ttl)
    
    def getset(self, key: str, value: Any) -> Optional[Any]:
        """获取并设置缓存"""
        old_value = self.get(key)
        self.set(key, value)
        return old_value
    
    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """增加数值"""
        try:
            current_value = self.get(key)
            if current_value is None:
                new_value = amount
            else:
                new_value = int(current_value) + amount
            
            self.set(key, new_value)
            return new_value
            
        except Exception as e:
            logger.error(f"增加数值失败: {e}")
            return None
    
    def decr(self, key: str, amount: int = 1) -> Optional[int]:
        """减少数值"""
        return self.incr(key, -amount)
    
    def hset(self, key: str, field: str, value: Any) -> bool:
        """设置哈希字段"""
        try:
            hash_data = self.get(key) or {}
            if not isinstance(hash_data, dict):
                hash_data = {}
            
            hash_data[field] = value
            return self.set(key, hash_data)
            
        except Exception as e:
            logger.error(f"设置哈希字段失败: {e}")
            return False
    
    def hget(self, key: str, field: str) -> Optional[Any]:
        """获取哈希字段"""
        try:
            hash_data = self.get(key)
            if isinstance(hash_data, dict):
                return hash_data.get(field)
            return None
            
        except Exception as e:
            logger.error(f"获取哈希字段失败: {e}")
            return None
    
    def hgetall(self, key: str) -> Dict[str, Any]:
        """获取所有哈希字段"""
        try:
            hash_data = self.get(key)
            if isinstance(hash_data, dict):
                return hash_data.copy()
            return {}
            
        except Exception as e:
            logger.error(f"获取所有哈希字段失败: {e}")
            return {}


# 全局实例
lightweight_cache_service = LightweightCacheService() 