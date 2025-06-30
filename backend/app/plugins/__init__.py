"""
插件系统
"""
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PluginBase(ABC):
    """插件基类"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.description = "插件描述"
        self.version = "1.0.0"
        self.author = "MetaBox"
        self.enabled = True
        self.created_at = datetime.utcnow()
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行插件功能"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """获取插件参数模式"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "enabled": self.enabled,
            "parameters": self.get_parameters()
        }
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取插件参数定义"""
        return {}

class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
    
    def register_plugin(self, plugin: PluginBase) -> bool:
        """注册插件"""
        try:
            if plugin.name in self.plugins:
                logger.warning(f"插件 {plugin.name} 已存在，将被覆盖")
            
            self.plugins[plugin.name] = plugin
            logger.info(f"插件 {plugin.name} 注册成功")
            return True
        except Exception as e:
            logger.error(f"插件 {plugin.name} 注册失败: {e}")
            return False
    
    def unregister_plugin(self, plugin_name: str) -> bool:
        """注销插件"""
        if plugin_name in self.plugins:
            del self.plugins[plugin_name]
            logger.info(f"插件 {plugin_name} 注销成功")
            return True
        return False
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """获取插件"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """获取所有插件信息"""
        return [
            {
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "author": plugin.author,
                "enabled": plugin.enabled,
                "created_at": plugin.created_at.isoformat()
            }
            for plugin in self.plugins.values()
        ]
    
    async def execute_plugin(self, plugin_name: str, **kwargs) -> Dict[str, Any]:
        """执行插件"""
        plugin = self.get_plugin(plugin_name)
        if not plugin:
            return {
                "success": False,
                "error": f"插件 {plugin_name} 不存在"
            }
        
        if not plugin.enabled:
            return {
                "success": False,
                "error": f"插件 {plugin_name} 已禁用"
            }
        
        try:
            result = await plugin.execute(**kwargs)
            return {
                "success": True,
                "plugin_name": plugin_name,
                "result": result,
                "executed_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"插件 {plugin_name} 执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "plugin_name": plugin_name
            }
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """启用插件"""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        plugin = self.get_plugin(plugin_name)
        if plugin:
            plugin.enabled = False
            return True
        return False

# 全局插件管理器实例
plugin_manager = PluginManager() 