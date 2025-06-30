"""
Agent推理服务
"""
from typing import List, Dict, Any, Optional
import asyncio
import json
import logging
from datetime import datetime

from app.plugins import plugin_manager, PluginBase
from app.services.vector_service import VectorService
from app.core.config import settings

logger = logging.getLogger(__name__)

class AgentService:
    """Agent推理服务"""
    
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.max_steps = 10  # 最大推理步数
    
    async def execute_agent_task(
        self, 
        task: str, 
        kb_ids: Optional[List[str]] = None,
        available_plugins: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """执行Agent任务"""
        try:
            # 初始化推理状态
            reasoning_steps = []
            current_context = {
                "task": task,
                "available_plugins": available_plugins or [],
                "knowledge_base_ids": kb_ids or [],
                "step_count": 0,
                "results": []
            }
            
            # 开始推理循环
            for step in range(self.max_steps):
                current_context["step_count"] = step + 1
                
                # 分析当前任务和上下文
                analysis = await self._analyze_task(current_context)
                reasoning_steps.append({
                    "step": step + 1,
                    "action": analysis["action"],
                    "reasoning": analysis["reasoning"],
                    "parameters": analysis.get("parameters", {})
                })
                
                # 执行动作
                if analysis["action"] == "search_knowledge":
                    result = await self._search_knowledge(
                        analysis["parameters"]["query"], 
                        kb_ids
                    )
                    current_context["results"].append({
                        "type": "knowledge_search",
                        "result": result
                    })
                
                elif analysis["action"] == "call_plugin":
                    result = await plugin_manager.execute_plugin(
                        analysis["parameters"]["plugin_name"],
                        **analysis["parameters"]["plugin_args"]
                    )
                    current_context["results"].append({
                        "type": "plugin_call",
                        "result": result
                    })
                
                elif analysis["action"] == "generate_response":
                    # 生成最终回答
                    final_response = await self._generate_final_response(
                        current_context, reasoning_steps
                    )
                    return {
                        "success": True,
                        "task": task,
                        "reasoning_steps": reasoning_steps,
                        "final_response": final_response,
                        "total_steps": step + 1,
                        "executed_at": datetime.utcnow().isoformat()
                    }
                
                elif analysis["action"] == "stop":
                    # 停止推理
                    break
            
            # 达到最大步数，生成回答
            final_response = await self._generate_final_response(
                current_context, reasoning_steps
            )
            return {
                "success": True,
                "task": task,
                "reasoning_steps": reasoning_steps,
                "final_response": final_response,
                "total_steps": self.max_steps,
                "warning": "达到最大推理步数",
                "executed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Agent任务执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "task": task
            }
    
    async def _analyze_task(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析当前任务，决定下一步动作"""
        task = context["task"]
        step_count = context["step_count"]
        available_plugins = context["available_plugins"]
        
        # 简单的任务分析逻辑
        # 实际项目中应该使用LLM进行智能分析
        
        # 检查是否需要搜索知识库
        if "搜索" in task or "查找" in task or "知识" in task:
            return {
                "action": "search_knowledge",
                "reasoning": f"任务涉及搜索，需要查询知识库",
                "parameters": {
                    "query": task
                }
            }
        
        # 检查是否需要调用插件
        if available_plugins:
            for plugin_name in available_plugins:
                if plugin_name.lower() in task.lower():
                    return {
                        "action": "call_plugin",
                        "reasoning": f"任务需要调用插件 {plugin_name}",
                        "parameters": {
                            "plugin_name": plugin_name,
                            "plugin_args": self._extract_plugin_args(task, plugin_name)
                        }
                    }
        
        # 检查是否包含数学计算
        if any(op in task for op in ["+", "-", "*", "/", "计算", "等于"]):
            return {
                "action": "call_plugin",
                "reasoning": "任务涉及数学计算，调用计算器插件",
                "parameters": {
                    "plugin_name": "CalculatorPlugin",
                    "plugin_args": {
                        "expression": self._extract_math_expression(task)
                    }
                }
            }
        
        # 检查是否包含天气查询
        if "天气" in task or "温度" in task:
            return {
                "action": "call_plugin",
                "reasoning": "任务涉及天气查询，调用天气插件",
                "parameters": {
                    "plugin_name": "WeatherPlugin",
                    "plugin_args": {
                        "city": self._extract_city_name(task)
                    }
                }
            }
        
        # 如果已经收集了足够信息，生成回答
        if step_count >= 2 or len(context["results"]) > 0:
            return {
                "action": "generate_response",
                "reasoning": "已收集足够信息，生成最终回答"
            }
        
        # 默认搜索知识库
        return {
            "action": "search_knowledge",
            "reasoning": "默认搜索知识库获取相关信息",
            "parameters": {
                "query": task
            }
        }
    
    async def _search_knowledge(self, query: str, kb_ids: List[str]) -> Dict[str, Any]:
        """搜索知识库"""
        if not kb_ids:
            return {
                "success": False,
                "error": "未指定知识库"
            }
        
        try:
            results = await self.vector_service.hybrid_search(query, kb_ids)
            return {
                "success": True,
                "query": query,
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_final_response(
        self, 
        context: Dict[str, Any], 
        reasoning_steps: List[Dict[str, Any]]
    ) -> str:
        """生成最终回答"""
        task = context["task"]
        results = context["results"]
        
        # 简单的回答生成逻辑
        # 实际项目中应该使用LLM生成更智能的回答
        
        response_parts = [f"关于任务「{task}」的回答：\n"]
        
        for result in results:
            if result["type"] == "knowledge_search" and result["result"]["success"]:
                search_results = result["result"]["results"]
                if search_results["text"]:
                    response_parts.append("📚 知识库搜索结果：")
                    for i, text_result in enumerate(search_results["text"][:2], 1):
                        response_parts.append(f"{i}. {text_result['content'][:100]}...")
                    response_parts.append("")
            
            elif result["type"] == "plugin_call" and result["result"]["success"]:
                plugin_result = result["result"]["result"]
                response_parts.append(f"🔧 插件执行结果：{plugin_result}")
                response_parts.append("")
        
        if len(response_parts) == 1:
            response_parts.append("抱歉，未能找到相关信息或执行相关操作。")
        
        return "\n".join(response_parts)
    
    def _extract_plugin_args(self, task: str, plugin_name: str) -> Dict[str, Any]:
        """提取插件参数"""
        # 简单的参数提取逻辑
        if plugin_name == "CalculatorPlugin":
            return {
                "expression": self._extract_math_expression(task)
            }
        elif plugin_name == "WeatherPlugin":
            return {
                "city": self._extract_city_name(task)
            }
        return {}
    
    def _extract_math_expression(self, task: str) -> str:
        """提取数学表达式"""
        import re
        # 简单的数学表达式提取
        math_pattern = r'(\d+[\+\-\*\/]\d+)'
        match = re.search(math_pattern, task)
        if match:
            return match.group(1)
        return "2+2"  # 默认表达式
    
    def _extract_city_name(self, task: str) -> str:
        """提取城市名称"""
        # 简单的城市名称提取
        cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉"]
        for city in cities:
            if city in task:
                return city
        return "北京"  # 默认城市 