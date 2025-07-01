from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.admin_service import AdminService
from app.schemas.admin import (
    SuperAdminCreate, SuperAdminLogin, SuperAdminResponse,
    ModelProviderCreate, ModelProviderUpdate, ModelProviderResponse,
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    SystemConfigCreate, SystemConfigUpdate, SystemConfigResponse,
    AdminDashboardStats
)
from app.core.auth import get_current_super_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["超级管理员"])

# 超级管理员认证相关
@router.post("/login", response_model=dict)
async def admin_login(
    login_data: SuperAdminLogin,
    db: Session = Depends(get_db)
):
    """超级管理员登录"""
    try:
        admin_service = AdminService(db)
        token = admin_service.authenticate_super_admin(login_data)
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
        
        return {
            "success": True,
            "data": {
                "token": token,
                "message": "登录成功"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败"
        )

@router.post("/create", response_model=dict)
async def create_super_admin(
    admin_data: SuperAdminCreate,
    db: Session = Depends(get_db)
):
    """创建超级管理员（仅首次使用）"""
    try:
        admin_service = AdminService(db)
        admin = admin_service.create_super_admin(admin_data)
        
        return {
            "success": True,
            "data": {
                "id": admin.id,
                "username": admin.username,
                "email": admin.email,
                "message": "超级管理员创建成功"
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建超级管理员失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建失败"
        )

# 仪表板
@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """获取仪表板统计信息"""
    try:
        admin_service = AdminService(db)
        stats = admin_service.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"获取仪表板统计失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取统计信息失败"
        )

# 模型供应商管理
@router.get("/model-providers", response_model=List[ModelProviderResponse])
async def get_model_providers(
    provider_type: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """获取模型供应商列表"""
    try:
        admin_service = AdminService(db)
        providers = admin_service.get_model_providers(provider_type, active_only)
        return providers
    except Exception as e:
        logger.error(f"获取模型供应商列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取供应商列表失败"
        )

@router.post("/model-providers", response_model=ModelProviderResponse)
async def create_model_provider(
    provider_data: ModelProviderCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """创建模型供应商"""
    try:
        admin_service = AdminService(db)
        provider = admin_service.create_model_provider(provider_data)
        return provider
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建模型供应商失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建供应商失败"
        )

@router.get("/model-providers/{provider_id}", response_model=ModelProviderResponse)
async def get_model_provider(
    provider_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """获取模型供应商详情"""
    try:
        admin_service = AdminService(db)
        provider = admin_service.get_model_provider_by_id(provider_id)
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        return provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模型供应商详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取供应商详情失败"
        )

@router.put("/model-providers/{provider_id}", response_model=ModelProviderResponse)
async def update_model_provider(
    provider_id: str,
    update_data: ModelProviderUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """更新模型供应商"""
    try:
        admin_service = AdminService(db)
        provider = admin_service.update_model_provider(provider_id, update_data)
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        return provider
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模型供应商失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新供应商失败"
        )

@router.delete("/model-providers/{provider_id}")
async def delete_model_provider(
    provider_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """删除模型供应商"""
    try:
        admin_service = AdminService(db)
        success = admin_service.delete_model_provider(provider_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        return {
            "success": True,
            "data": {
                "message": "供应商删除成功"
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模型供应商失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除供应商失败"
        )

@router.post("/model-providers/{provider_id}/test")
async def test_model_provider(
    provider_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """测试模型供应商连接"""
    try:
        admin_service = AdminService(db)
        api_key = admin_service.get_provider_api_key(provider_id)
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="供应商不存在"
            )
        
        # TODO: 实现实际的连接测试逻辑
        # 这里可以调用不同供应商的API进行测试
        
        return {
            "success": True,
            "data": {
                "message": "连接测试成功",
                "status": "connected"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"测试模型供应商连接失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="连接测试失败"
        )

# 模型配置管理
@router.get("/model-configs", response_model=List[ModelConfigResponse])
async def get_model_configs(
    provider_id: str = None,
    model_type: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """获取模型配置列表"""
    try:
        admin_service = AdminService(db)
        configs = admin_service.get_model_configs(provider_id, model_type, active_only)
        return configs
    except Exception as e:
        logger.error(f"获取模型配置列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取模型配置失败"
        )

@router.post("/model-configs", response_model=ModelConfigResponse)
async def create_model_config(
    config_data: ModelConfigCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """创建模型配置"""
    try:
        admin_service = AdminService(db)
        config = admin_service.create_model_config(config_data)
        return config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建模型配置失败"
        )

@router.put("/model-configs/{config_id}", response_model=ModelConfigResponse)
async def update_model_config(
    config_id: str,
    update_data: ModelConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """更新模型配置"""
    try:
        admin_service = AdminService(db)
        config = admin_service.update_model_config(config_id, update_data)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模型配置不存在"
            )
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新模型配置失败"
        )

@router.delete("/model-configs/{config_id}")
async def delete_model_config(
    config_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """删除模型配置"""
    try:
        admin_service = AdminService(db)
        success = admin_service.delete_model_config(config_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="模型配置不存在"
            )
        
        return {
            "success": True,
            "data": {
                "message": "模型配置删除成功"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除模型配置失败"
        )

# 系统配置管理
@router.get("/system-configs", response_model=List[SystemConfigResponse])
async def get_system_configs(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """获取所有系统配置"""
    try:
        admin_service = AdminService(db)
        configs = admin_service.get_all_system_configs()
        return configs
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统配置失败"
        )

@router.get("/system-configs/{key}")
async def get_system_config(
    key: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """获取系统配置值"""
    try:
        admin_service = AdminService(db)
        value = admin_service.get_system_config(key)
        
        if value is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="配置不存在"
            )
        
        return {
            "success": True,
            "data": {
                "key": key,
                "value": value
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取配置失败"
        )

@router.post("/system-configs", response_model=SystemConfigResponse)
async def create_system_config(
    config_data: SystemConfigCreate,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """创建系统配置"""
    try:
        admin_service = AdminService(db)
        config = admin_service.create_system_config(config_data)
        return config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"创建系统配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建系统配置失败"
        )

@router.put("/system-configs/{key}")
async def update_system_config(
    key: str,
    value: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_super_admin)
):
    """更新系统配置"""
    try:
        admin_service = AdminService(db)
        success = admin_service.update_system_config(key, value)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="系统配置不存在"
            )
        
        return {
            "success": True,
            "data": {
                "key": key,
                "message": "系统配置更新成功"
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新系统配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新配置失败"
        ) 