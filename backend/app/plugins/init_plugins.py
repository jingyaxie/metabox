"""
插件初始化脚本
"""
import logging
from app.plugins import plugin_manager
from app.plugins.weather_plugin import WeatherPlugin
from app.plugins.calculator_plugin import CalculatorPlugin

logger = logging.getLogger(__name__)

def init_plugins():
    """初始化所有插件"""
    try:
        # 注册天气插件
        weather_plugin = WeatherPlugin()
        plugin_manager.register_plugin(weather_plugin)
        logger.info("天气插件注册成功")
        
        # 注册计算器插件
        calculator_plugin = CalculatorPlugin()
        plugin_manager.register_plugin(calculator_plugin)
        logger.info("计算器插件注册成功")
        
        logger.info(f"插件初始化完成，共注册 {len(plugin_manager.plugins)} 个插件")
        return True
        
    except Exception as e:
        logger.error(f"插件初始化失败: {e}")
        return False

def get_available_plugins():
    """获取可用插件列表"""
    return list(plugin_manager.plugins.keys()) 