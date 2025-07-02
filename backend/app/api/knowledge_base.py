"""
知识库管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.admin_service import AdminService
from app.schemas.knowledge_base import SmartConfigRequest, SmartConfigResponse
from app.services.text_splitter import SmartConfigManager

router = APIRouter()

@router.get("/models")
async def get_available_models(
    model_type: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取可用的模型列表（用于知识库创建）"""
    try:
        admin_service = AdminService(db)
        
        # 获取所有活跃的模型配置
        model_configs = admin_service.get_model_configs(
            model_type=model_type,
            active_only=True
        )
        
        # 转换为前端需要的格式
        models = {
            "chat": [],      # 聊天模型
            "embedding": [], # 嵌入模型
            "image": []      # 图片模型
        }
        
        for config in model_configs:
            # 获取供应商信息
            provider = admin_service.get_model_provider_by_id(config.provider_id)
            if provider and provider.is_active:
                model_info = {
                    "id": config.id,
                    "name": config.display_name,
                    "model_name": config.model_name,
                    "provider": provider.display_name,
                    "provider_type": provider.provider_type,
                    "model_type": config.model_type,
                    "max_tokens": config.max_tokens,
                    "temperature": config.temperature,
                    "is_default": config.is_default,
                    "description": f"{provider.display_name} - {config.display_name}"
                }
                
                # 根据模型类型分类
                if config.model_type == "chat":
                    models["chat"].append(model_info)
                elif config.model_type == "embedding":
                    models["embedding"].append(model_info)
                elif config.model_type == "image":
                    models["image"].append(model_info)
        
        return models
        
    except Exception as e:
        # 如果出错，返回默认模型
        return {
            "chat": [
                {
                    "id": "default-chat",
                    "name": "GPT-3.5 Turbo",
                    "model_name": "gpt-3.5-turbo",
                    "provider": "OpenAI",
                    "provider_type": "openai",
                    "model_type": "chat",
                    "max_tokens": 4096,
                    "temperature": "0.7",
                    "is_default": True,
                    "description": "OpenAI - GPT-3.5 Turbo"
                }
            ],
            "embedding": [
                {
                    "id": "default-embedding",
                    "name": "text-embedding-ada-002",
                    "model_name": "text-embedding-ada-002",
                    "provider": "OpenAI",
                    "provider_type": "openai",
                    "model_type": "embedding",
                    "max_tokens": None,
                    "temperature": None,
                    "is_default": True,
                    "description": "OpenAI - text-embedding-ada-002"
                }
            ],
            "image": []
        }

@router.get("/")
async def get_knowledge_bases(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库列表"""
    kb_service = KnowledgeBaseService(db)
    
    # 获取用户的知识库
    knowledge_bases = kb_service.get_user_knowledge_bases(current_user.id)
    return knowledge_bases

@router.post("/")
async def create_knowledge_base(
    name: str,
    description: Optional[str] = None,
    kb_type: str = "text",
    text_model_id: Optional[str] = None,
    image_model_id: Optional[str] = None,
    embedding_model_id: Optional[str] = None,
    image_embedding_model_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建知识库"""
    kb_service = KnowledgeBaseService(db)
    
    # 创建知识库
    knowledge_base = kb_service.create_knowledge_base(
        name=name,
        description=description,
        kb_type=kb_type,
        owner_id=current_user.id,
        text_model_id=text_model_id,
        image_model_id=image_model_id,
        embedding_model_id=embedding_model_id,
        image_embedding_model_id=image_embedding_model_id
    )
    
    return knowledge_base

@router.get("/{kb_id}")
async def get_knowledge_base(
    kb_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取知识库详情"""
    kb_service = KnowledgeBaseService(db)
    admin_service = AdminService(db)
    
    # 获取知识库
    knowledge_base = kb_service.get_knowledge_base_by_id(kb_id, current_user.id)
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在或无权限访问"
        )
    
    # 获取模型详细信息
    kb_data = knowledge_base.__dict__.copy()
    kb_data['text_model_info'] = None
    kb_data['image_model_info'] = None
    kb_data['embedding_model_info'] = None
    kb_data['image_embedding_model_info'] = None
    
    if knowledge_base.text_model_id:
        text_model = admin_service.get_model_config_by_id(knowledge_base.text_model_id)
        if text_model:
            provider = admin_service.get_model_provider_by_id(text_model.provider_id)
            kb_data['text_model_info'] = {
                "id": text_model.id,
                "name": text_model.display_name,
                "provider": provider.display_name if provider else "Unknown",
                "model_type": text_model.model_type
            }
    
    if knowledge_base.image_model_id:
        image_model = admin_service.get_model_config_by_id(knowledge_base.image_model_id)
        if image_model:
            provider = admin_service.get_model_provider_by_id(image_model.provider_id)
            kb_data['image_model_info'] = {
                "id": image_model.id,
                "name": image_model.display_name,
                "provider": provider.display_name if provider else "Unknown",
                "model_type": image_model.model_type
            }
    
    if knowledge_base.embedding_model_id:
        embedding_model = admin_service.get_model_config_by_id(knowledge_base.embedding_model_id)
        if embedding_model:
            provider = admin_service.get_model_provider_by_id(embedding_model.provider_id)
            kb_data['embedding_model_info'] = {
                "id": embedding_model.id,
                "name": embedding_model.display_name,
                "provider": provider.display_name if provider else "Unknown",
                "model_type": embedding_model.model_type
            }
    
    if knowledge_base.image_embedding_model_id:
        image_embedding_model = admin_service.get_model_config_by_id(knowledge_base.image_embedding_model_id)
        if image_embedding_model:
            provider = admin_service.get_model_provider_by_id(image_embedding_model.provider_id)
            kb_data['image_embedding_model_info'] = {
                "id": image_embedding_model.id,
                "name": image_embedding_model.display_name,
                "provider": provider.display_name if provider else "Unknown",
                "model_type": image_embedding_model.model_type
            }
    
    return kb_data

@router.put("/{kb_id}")
async def update_knowledge_base(
    kb_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    kb_type: Optional[str] = None,
    text_model_id: Optional[str] = None,
    image_model_id: Optional[str] = None,
    embedding_model_id: Optional[str] = None,
    image_embedding_model_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新知识库"""
    kb_service = KnowledgeBaseService(db)
    
    # 更新知识库
    knowledge_base = kb_service.update_knowledge_base(
        kb_id=kb_id,
        user_id=current_user.id,
        name=name,
        description=description,
        kb_type=kb_type,
        text_model_id=text_model_id,
        image_model_id=image_model_id,
        embedding_model_id=embedding_model_id,
        image_embedding_model_id=image_embedding_model_id
    )
    
    if not knowledge_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在或无权限更新"
        )
    
    return knowledge_base

@router.post("/{kb_id}/upload")
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """上传文档到知识库"""
    kb_service = KnowledgeBaseService(db)
    
    # 上传文档
    result = await kb_service.upload_document(kb_id, file, current_user.id)
    return result

@router.delete("/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除知识库"""
    kb_service = KnowledgeBaseService(db)
    
    # 删除知识库
    success = kb_service.delete_knowledge_base(kb_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库不存在或无权限删除"
        )
    
    return {"message": "知识库删除成功"}

@router.post("/smart-config")
async def get_smart_config(
    request: SmartConfigRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取智能配置建议"""
    config_manager = SmartConfigManager()
    
    # 获取配置建议
    config = config_manager.get_smart_config(
        file_type=request.file_type,
        file_size=request.file_size,
        content_length=request.content_length,
        chunk_size=request.chunk_size,
        chunk_overlap=request.chunk_overlap
    )
    
    return SmartConfigResponse(**config) 