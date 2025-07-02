"""
轻量级存储服务
使用本地文件存储，降低资源消耗
"""

import os
import logging
import shutil
import hashlib
from typing import Optional, List, Dict, Any, BinaryIO
from datetime import datetime
import aiofiles
import mimetypes

from app.core.lightweight_config import lightweight_config

logger = logging.getLogger(__name__)


class LightweightStorageService:
    """轻量级存储服务"""
    
    def __init__(self):
        self.config = lightweight_config.get_storage_config()
        self.upload_dir = self.config["upload_dir"]
        self.max_file_size = self.config["max_file_size"]
        
        # 确保上传目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # 文件缓存
        self.file_cache = {}
        self.max_cache_size = 100  # 降低缓存大小
    
    async def save_file(
        self, 
        file_content: bytes, 
        filename: str, 
        content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """保存文件"""
        try:
            # 检查文件大小
            if len(file_content) > self.max_file_size:
                raise ValueError(f"文件大小超过限制: {len(file_content)} > {self.max_file_size}")
            
            # 生成文件路径
            file_path = await self._generate_file_path(filename)
            
            # 保存文件
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            # 获取文件信息
            file_info = await self._get_file_info(file_path, filename, content_type)
            
            # 缓存文件信息
            self._cache_file_info(file_info)
            
            logger.info(f"文件保存成功: {file_path}")
            return file_info
            
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            raise
    
    async def read_file(self, file_id: str) -> Optional[bytes]:
        """读取文件"""
        try:
            file_path = await self._get_file_path(file_id)
            if not file_path or not os.path.exists(file_path):
                return None
            
            async with aiofiles.open(file_path, 'rb') as f:
                content = await f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"读取文件失败: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        try:
            file_path = await self._get_file_path(file_id)
            if not file_path or not os.path.exists(file_path):
                return False
            
            os.remove(file_path)
            
            # 清理缓存
            if file_id in self.file_cache:
                del self.file_cache[file_id]
            
            logger.info(f"文件删除成功: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    
    async def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        try:
            # 检查缓存
            if file_id in self.file_cache:
                return self.file_cache[file_id]
            
            file_path = await self._get_file_path(file_id)
            if not file_path or not os.path.exists(file_path):
                return None
            
            # 获取文件信息
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            file_info = {
                "id": file_id,
                "filename": filename,
                "path": file_path,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
                "content_type": mimetypes.guess_type(filename)[0] or "application/octet-stream"
            }
            
            # 缓存文件信息
            self._cache_file_info(file_info)
            
            return file_info
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            return None
    
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """列出文件"""
        try:
            files = []
            prefix_path = os.path.join(self.upload_dir, prefix)
            
            if os.path.exists(prefix_path):
                for root, dirs, filenames in os.walk(prefix_path):
                    for filename in filenames[:limit]:
                        file_path = os.path.join(root, filename)
                        rel_path = os.path.relpath(file_path, self.upload_dir)
                        
                        # 生成文件ID
                        file_id = self._generate_file_id(rel_path)
                        
                        # 获取文件信息
                        file_info = await self.get_file_info(file_id)
                        if file_info:
                            files.append(file_info)
            
            return files
            
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []
    
    async def file_exists(self, file_id: str) -> bool:
        """检查文件是否存在"""
        try:
            file_path = await self._get_file_path(file_id)
            return file_path is not None and os.path.exists(file_path)
        except Exception as e:
            logger.error(f"检查文件存在失败: {e}")
            return False
    
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """获取文件访问URL"""
        try:
            file_info = await self.get_file_info(file_id)
            if not file_info:
                return None
            
            # 返回相对路径URL
            return f"/uploads/{file_info['filename']}"
            
        except Exception as e:
            logger.error(f"获取文件URL失败: {e}")
            return None
    
    async def _generate_file_path(self, filename: str) -> str:
        """生成文件路径"""
        # 使用时间戳和哈希生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(f"{filename}_{timestamp}".encode()).hexdigest()[:8]
        
        # 获取文件扩展名
        _, ext = os.path.splitext(filename)
        
        # 生成新文件名
        new_filename = f"{timestamp}_{file_hash}{ext}"
        
        # 按日期分目录
        date_dir = datetime.now().strftime("%Y/%m/%d")
        date_path = os.path.join(self.upload_dir, date_dir)
        os.makedirs(date_path, exist_ok=True)
        
        return os.path.join(date_path, new_filename)
    
    async def _get_file_path(self, file_id: str) -> Optional[str]:
        """根据文件ID获取文件路径"""
        try:
            # 这里简化处理，实际应该维护文件ID到路径的映射
            # 可以通过数据库或配置文件来存储映射关系
            
            # 临时实现：遍历目录查找文件
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    if file_id in file:
                        return os.path.join(root, file)
            
            return None
            
        except Exception as e:
            logger.error(f"获取文件路径失败: {e}")
            return None
    
    async def _get_file_info(
        self, 
        file_path: str, 
        original_filename: str, 
        content_type: Optional[str]
    ) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            stat = os.stat(file_path)
            
            # 生成文件ID
            file_id = self._generate_file_id(file_path)
            
            return {
                "id": file_id,
                "filename": original_filename,
                "path": file_path,
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
                "content_type": content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
            }
            
        except Exception as e:
            logger.error(f"获取文件信息失败: {e}")
            raise
    
    def _generate_file_id(self, file_path: str) -> str:
        """生成文件ID"""
        # 使用文件路径的哈希作为文件ID
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _cache_file_info(self, file_info: Dict[str, Any]):
        """缓存文件信息"""
        try:
            self.file_cache[file_info["id"]] = file_info
            
            # 限制缓存大小
            if len(self.file_cache) > self.max_cache_size:
                # 删除最旧的缓存
                oldest_key = next(iter(self.file_cache))
                del self.file_cache[oldest_key]
                
        except Exception as e:
            logger.error(f"缓存文件信息失败: {e}")
    
    async def clear_cache(self):
        """清理缓存"""
        try:
            self.file_cache.clear()
            logger.info("存储服务缓存已清理")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        total_size += stat.st_size
                        file_count += 1
                    except:
                        continue
            
            return {
                "total_size": total_size,
                "file_count": file_count,
                "max_file_size": self.max_file_size,
                "cache_size": len(self.file_cache)
            }
            
        except Exception as e:
            logger.error(f"获取存储统计失败: {e}")
            return {}
    
    async def cleanup_old_files(self, days: int = 30) -> int:
        """清理旧文件"""
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            deleted_count = 0
            
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat = os.stat(file_path)
                        if stat.st_mtime < cutoff_time:
                            os.remove(file_path)
                            deleted_count += 1
                    except:
                        continue
            
            logger.info(f"清理了 {deleted_count} 个旧文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧文件失败: {e}")
            return 0


# 全局实例
lightweight_storage_service = LightweightStorageService() 