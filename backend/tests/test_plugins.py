"""
插件系统测试
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from app.plugins import PluginBase, PluginManager
from app.plugins.weather_plugin import WeatherPlugin
from app.plugins.calculator_plugin import CalculatorPlugin

class TestPlugin(PluginBase):
    """测试插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "TestPlugin"
        self.description = "测试插件"
        self.version = "1.0.0"
        self.author = "Test"
        self.enabled = True
    
    async def execute(self, **kwargs):
        return {"test": "success", "args": kwargs}

@pytest.fixture
def plugin_manager():
    """插件管理器实例"""
    return PluginManager()

@pytest.fixture
def test_plugin():
    """测试插件实例"""
    return TestPlugin()

class TestPluginBase:
    """测试插件基类"""
    
    def test_plugin_base_creation(self):
        """测试插件基类创建"""
        plugin = TestPlugin()
        assert plugin.name == "TestPlugin"
        assert plugin.description == "测试插件"
        assert plugin.version == "1.0.0"
        assert plugin.author == "Test"
        assert plugin.enabled is True
    
    def test_plugin_schema(self):
        """测试插件模式"""
        plugin = TestPlugin()
        schema = plugin.get_schema()
        assert schema["name"] == "TestPlugin"
        assert schema["description"] == "测试插件"
        assert schema["version"] == "1.0.0"
        assert schema["author"] == "Test"
        assert schema["enabled"] is True

class TestPluginManager:
    """测试插件管理器"""
    
    def test_register_plugin(self, plugin_manager, test_plugin):
        """测试插件注册"""
        success = plugin_manager.register_plugin(test_plugin)
        assert success is True
        assert "TestPlugin" in plugin_manager.plugins
        assert plugin_manager.plugins["TestPlugin"] == test_plugin
    
    def test_register_duplicate_plugin(self, plugin_manager, test_plugin):
        """测试重复注册插件"""
        plugin_manager.register_plugin(test_plugin)
        success = plugin_manager.register_plugin(test_plugin)
        assert success is True  # 应该覆盖而不是失败
    
    def test_unregister_plugin(self, plugin_manager, test_plugin):
        """测试插件注销"""
        plugin_manager.register_plugin(test_plugin)
        success = plugin_manager.unregister_plugin("TestPlugin")
        assert success is True
        assert "TestPlugin" not in plugin_manager.plugins
    
    def test_unregister_nonexistent_plugin(self, plugin_manager):
        """测试注销不存在的插件"""
        success = plugin_manager.unregister_plugin("NonexistentPlugin")
        assert success is False
    
    def test_get_plugin(self, plugin_manager, test_plugin):
        """测试获取插件"""
        plugin_manager.register_plugin(test_plugin)
        plugin = plugin_manager.get_plugin("TestPlugin")
        assert plugin == test_plugin
    
    def test_get_nonexistent_plugin(self, plugin_manager):
        """测试获取不存在的插件"""
        plugin = plugin_manager.get_plugin("NonexistentPlugin")
        assert plugin is None
    
    def test_get_all_plugins(self, plugin_manager, test_plugin):
        """测试获取所有插件"""
        plugin_manager.register_plugin(test_plugin)
        plugins = plugin_manager.get_all_plugins()
        assert len(plugins) == 1
        assert plugins[0]["name"] == "TestPlugin"
    
    @pytest.mark.asyncio
    async def test_execute_plugin(self, plugin_manager, test_plugin):
        """测试执行插件"""
        plugin_manager.register_plugin(test_plugin)
        result = await plugin_manager.execute_plugin("TestPlugin", arg1="value1")
        assert result["success"] is True
        assert result["plugin_name"] == "TestPlugin"
        assert result["result"]["test"] == "success"
        assert result["result"]["args"]["arg1"] == "value1"
    
    @pytest.mark.asyncio
    async def test_execute_nonexistent_plugin(self, plugin_manager):
        """测试执行不存在的插件"""
        result = await plugin_manager.execute_plugin("NonexistentPlugin")
        assert result["success"] is False
        assert "不存在" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_disabled_plugin(self, plugin_manager, test_plugin):
        """测试执行禁用的插件"""
        test_plugin.enabled = False
        plugin_manager.register_plugin(test_plugin)
        result = await plugin_manager.execute_plugin("TestPlugin")
        assert result["success"] is False
        assert "已禁用" in result["error"]
    
    def test_enable_plugin(self, plugin_manager, test_plugin):
        """测试启用插件"""
        test_plugin.enabled = False
        plugin_manager.register_plugin(test_plugin)
        success = plugin_manager.enable_plugin("TestPlugin")
        assert success is True
        assert test_plugin.enabled is True
    
    def test_disable_plugin(self, plugin_manager, test_plugin):
        """测试禁用插件"""
        plugin_manager.register_plugin(test_plugin)
        success = plugin_manager.disable_plugin("TestPlugin")
        assert success is True
        assert test_plugin.enabled is False

class TestWeatherPlugin:
    """测试天气插件"""
    
    @pytest.fixture
    def weather_plugin(self):
        return WeatherPlugin()
    
    def test_weather_plugin_creation(self, weather_plugin):
        """测试天气插件创建"""
        assert weather_plugin.name == "WeatherPlugin"
        assert weather_plugin.description == "查询指定城市的天气信息"
        assert weather_plugin.version == "1.0.0"
        assert weather_plugin.author == "MetaBox"
    
    def test_weather_plugin_parameters(self, weather_plugin):
        """测试天气插件参数"""
        parameters = weather_plugin.get_parameters()
        assert "city" in parameters
        assert "unit" in parameters
        assert parameters["city"]["required"] is True
        assert parameters["unit"]["default"] == "celsius"
    
    @pytest.mark.asyncio
    async def test_weather_plugin_execute(self, weather_plugin):
        """测试天气插件执行"""
        result = await weather_plugin.execute(city="北京", unit="celsius")
        assert result["success"] is True
        assert result["city"] == "北京"
        assert result["unit"] == "celsius"
        assert "weather" in result
    
    @pytest.mark.asyncio
    async def test_weather_plugin_missing_city(self, weather_plugin):
        """测试天气插件缺少城市参数"""
        result = await weather_plugin.execute(unit="celsius")
        assert result["success"] is False
        assert "城市名称不能为空" in result["error"]

class TestCalculatorPlugin:
    """测试计算器插件"""
    
    @pytest.fixture
    def calculator_plugin(self):
        return CalculatorPlugin()
    
    def test_calculator_plugin_creation(self, calculator_plugin):
        """测试计算器插件创建"""
        assert calculator_plugin.name == "CalculatorPlugin"
        assert calculator_plugin.description == "执行数学计算"
        assert calculator_plugin.version == "1.0.0"
        assert calculator_plugin.author == "MetaBox"
    
    def test_calculator_plugin_parameters(self, calculator_plugin):
        """测试计算器插件参数"""
        parameters = calculator_plugin.get_parameters()
        assert "expression" in parameters
        assert parameters["expression"]["required"] is True
    
    @pytest.mark.asyncio
    async def test_calculator_plugin_execute(self, calculator_plugin):
        """测试计算器插件执行"""
        result = await calculator_plugin.execute(expression="2+3")
        assert result["success"] is True
        assert result["expression"] == "2+3"
        assert result["result"] == 5
    
    @pytest.mark.asyncio
    async def test_calculator_plugin_missing_expression(self, calculator_plugin):
        """测试计算器插件缺少表达式参数"""
        result = await calculator_plugin.execute()
        assert result["success"] is False
        assert "表达式不能为空" in result["error"]
    
    @pytest.mark.asyncio
    async def test_calculator_plugin_invalid_expression(self, calculator_plugin):
        """测试计算器插件无效表达式"""
        result = await calculator_plugin.execute(expression="import os")
        assert result["success"] is False
        assert "不安全的字符" in result["error"] 