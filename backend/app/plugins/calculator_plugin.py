"""
计算器插件
"""
import re
from typing import Dict, Any
from . import PluginBase

class CalculatorPlugin(PluginBase):
    """计算器插件"""
    
    def __init__(self):
        super().__init__()
        self.name = "CalculatorPlugin"
        self.description = "执行数学计算"
        self.version = "1.0.0"
        self.author = "MetaBox"
    
    def get_parameters(self) -> Dict[str, Any]:
        """获取插件参数定义"""
        return {
            "expression": {
                "type": "string",
                "description": "数学表达式，如: 2 + 3 * 4",
                "required": True
            }
        }
    
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """执行计算"""
        expression = kwargs.get("expression")
        
        if not expression:
            return {
                "success": False,
                "error": "表达式不能为空"
            }
        
        try:
            # 清理表达式，只允许安全的数学运算
            clean_expression = self._sanitize_expression(expression)
            if not clean_expression:
                return {
                    "success": False,
                    "error": "表达式包含不安全的字符"
                }
            
            # 计算结果
            result = eval(clean_expression)
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"计算失败: {str(e)}"
            }
    
    def _sanitize_expression(self, expression: str) -> str:
        """清理表达式，只允许安全的数学运算"""
        # 移除所有空白字符
        expression = expression.replace(" ", "")
        
        # 只允许数字、运算符和括号
        allowed_chars = re.compile(r'^[0-9+\-*/().]+$')
        if not allowed_chars.match(expression):
            return ""
        
        # 检查括号匹配
        if expression.count('(') != expression.count(')'):
            return ""
        
        return expression 