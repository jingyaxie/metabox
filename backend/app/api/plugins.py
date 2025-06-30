"""
插件管理API
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.plugins import plugin_manager
from app.services.agent_service import AgentService
from app.services.vector_service import VectorService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/plugins", tags=["插件管理"])

class PluginExecuteRequest(BaseModel):
    """插件执行请求"""
    plugin_name: str
    parameters: Dict[str, Any] = {}

class AgentTaskRequest(BaseModel):
    """Agent任务请求"""
    task: str
    kb_ids: List[str] = []
    available_plugins: List[str] = []

class PluginInfo(BaseModel):
    """插件信息"""
    name: str
    description: str
    version: str
    author: str
    enabled: bool
    created_at: str

@router.get("/", response_model=List[PluginInfo])
async def get_plugins(current_user: User = Depends(get_current_user)):
    """获取所有插件列表"""
    try:
        plugins = plugin_manager.get_all_plugins()
        return [PluginInfo(**plugin) for plugin in plugins]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取插件列表失败: {str(e)}"
        )

@router.get("/{plugin_name}")
async def get_plugin_info(
    plugin_name: str,
    current_user: User = Depends(get_current_user)
):
    """获取插件详细信息"""
    try:
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"插件 {plugin_name} 不存在"
            )
        
        return {
            "success": True,
            "data": plugin.get_schema()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取插件信息失败: {str(e)}"
        )

@router.post("/{plugin_name}/execute")
async def execute_plugin(
    plugin_name: str,
    request: PluginExecuteRequest,
    current_user: User = Depends(get_current_user)
):
    """执行插件"""
    try:
        result = await plugin_manager.execute_plugin(
            plugin_name, 
            **request.parameters
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行插件失败: {str(e)}"
        )

@router.post("/{plugin_name}/enable")
async def enable_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_user)
):
    """启用插件"""
    try:
        success = plugin_manager.enable_plugin(plugin_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"插件 {plugin_name} 不存在"
            )
        
        return {
            "success": True,
            "message": f"插件 {plugin_name} 已启用"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启用插件失败: {str(e)}"
        )

@router.post("/{plugin_name}/disable")
async def disable_plugin(
    plugin_name: str,
    current_user: User = Depends(get_current_user)
):
    """禁用插件"""
    try:
        success = plugin_manager.disable_plugin(plugin_name)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"插件 {plugin_name} 不存在"
            )
        
        return {
            "success": True,
            "message": f"插件 {plugin_name} 已禁用"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"禁用插件失败: {str(e)}"
        )

@router.post("/agent/task")
async def create_agent_task(
    request: AgentTaskRequest,
    current_user: User = Depends(get_current_user)
):
    """创建Agent任务"""
    try:
        agent_service = AgentService()
        task = await agent_service.create_task(
            user_id=current_user.id,
            task=request.task,
            kb_ids=request.kb_ids,
            available_plugins=request.available_plugins
        )
        
        return {
            "success": True,
            "data": task
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建Agent任务失败: {str(e)}"
        )

@router.get("/agent/task/{task_id}")
async def get_agent_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取Agent任务状态"""
    try:
        agent_service = AgentService()
        task = await agent_service.get_task(task_id, current_user.id)
        
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="任务不存在"
            )
        
        return {
            "success": True,
            "data": task
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务状态失败: {str(e)}"
        )

@router.get("/agent/tasks")
async def get_agent_tasks(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """获取用户的任务列表"""
    try:
        agent_service = AgentService()
        tasks = await agent_service.get_user_tasks(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": tasks
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取任务列表失败: {str(e)}"
        )

@router.post("/agent/execute")
async def execute_agent_task(
    request: AgentTaskRequest,
    current_user: User = Depends(get_current_user)
):
    """执行Agent任务"""
    try:
        # 初始化服务
        vector_service = VectorService()
        agent_service = AgentService(vector_service)
        
        result = await agent_service.execute_agent_task(
            task=request.task,
            kb_ids=request.kb_ids,
            available_plugins=request.available_plugins
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"执行Agent任务失败: {str(e)}"
        ) 