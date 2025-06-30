"""
智能配置 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.smart_config import SmartConfigService
from app.schemas.smart_config import (
    SmartConfigRequest,
    SmartConfigResponse,
    ConfigTemplate,
    ConfigTemplateCreate,
    ConfigTemplateUpdate,
    BatchConfigRequest,
    BatchConfigResponse,
    ConfigPreview
)

router = APIRouter()
security = HTTPBearer()


@router.post("/smart-config", response_model=SmartConfigResponse)
async def get_smart_config(
    request: SmartConfigRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取智能配置推荐"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取智能配置
    response = await smart_config_service.get_smart_config(request)
    
    return response


@router.post("/smart-config/validate")
async def validate_custom_config(
    chunk_size: int,
    chunk_overlap: int,
    embedding_model: str,
    similarity_threshold: float,
    max_tokens: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """验证自定义配置参数"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 验证配置
    validation = await smart_config_service.validate_custom_config(
        chunk_size, chunk_overlap, embedding_model,
        similarity_threshold, max_tokens
    )
    
    return validation


@router.post("/smart-config/preview", response_model=ConfigPreview)
async def get_config_preview(
    content: str,
    config: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取配置预览"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取预览
    preview = await smart_config_service.get_config_preview(content, config)
    
    return preview


# 配置模板管理
@router.post("/smart-config/templates", response_model=ConfigTemplate)
async def create_config_template(
    template: ConfigTemplateCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """创建配置模板"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 创建模板
    new_template = await smart_config_service.create_template(template)
    
    return new_template


@router.get("/smart-config/templates", response_model=List[ConfigTemplate])
async def list_config_templates(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取配置模板列表"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取模板列表
    templates = await smart_config_service.list_templates()
    
    return templates


@router.get("/smart-config/templates/{template_id}", response_model=ConfigTemplate)
async def get_config_template(
    template_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取配置模板详情"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 获取模板
    template = await smart_config_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置模板不存在"
        )
    
    return template


@router.put("/smart-config/templates/{template_id}", response_model=ConfigTemplate)
async def update_config_template(
    template_id: str,
    update_data: ConfigTemplateUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """更新配置模板"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 更新模板
    updated_template = await smart_config_service.update_template(template_id, update_data)
    if not updated_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置模板不存在"
        )
    
    return updated_template


@router.delete("/smart-config/templates/{template_id}")
async def delete_config_template(
    template_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """删除配置模板"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 删除模板
    success = await smart_config_service.delete_template(template_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置模板不存在"
        )
    
    return {"message": "配置模板删除成功"}


@router.post("/smart-config/templates/{template_id}/apply", response_model=SmartConfigResponse)
async def apply_config_template(
    template_id: str,
    content: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """应用配置模板"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 应用模板
    response = await smart_config_service.apply_template(template_id, content)
    
    return response


@router.post("/smart-config/batch", response_model=BatchConfigResponse)
async def batch_configure(
    batch_request: BatchConfigRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """批量配置"""
    auth_service = AuthService(db)
    smart_config_service = SmartConfigService()
    
    # 验证当前用户
    current_user = auth_service.get_current_user(credentials.credentials)
    
    # 批量配置
    response = await smart_config_service.batch_configure(batch_request)
    
    return response 