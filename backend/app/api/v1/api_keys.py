from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.api_key import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeyListResponse,
    ApiKeyUsageListResponse,
    ApiKeyQuotaListResponse
)
from app.services.api_key_service import ApiKeyService
from app.models.user import User

router = APIRouter(prefix="/api/v1/api-keys", tags=["api-keys"])


@router.post("/", response_model=dict)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建API密钥"""
    try:
        api_key_service = ApiKeyService(db)
        key, api_key_response = api_key_service.create_api_key(
            api_key_data=api_key_data,
            user_id=current_user.id
        )
        
        return {
            "success": True,
            "data": {
                "api_key": key,  # 只在创建时返回完整密钥
                "api_key_info": api_key_response
            },
            "message": "API密钥创建成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "CREATE_FAILED",
                    "message": f"创建API密钥失败: {str(e)}"
                }
            }
        )


@router.get("/", response_model=ApiKeyListResponse)
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的API密钥列表"""
    try:
        api_key_service = ApiKeyService(db)
        api_keys = api_key_service.get_api_keys_by_user(current_user.id)
        
        return ApiKeyListResponse(
            api_keys=api_keys,
            total=len(api_keys)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "LIST_FAILED",
                    "message": f"获取API密钥列表失败: {str(e)}"
                }
            }
        )


@router.get("/{api_key_id}", response_model=ApiKeyResponse)
async def get_api_key(
    api_key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取API密钥详情"""
    try:
        api_key_service = ApiKeyService(db)
        api_key = api_key_service.get_api_key_by_id(api_key_id)
        
        if not api_key:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "API密钥不存在"
                    }
                }
            )
        
        # 检查权限
        if api_key.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": "没有访问权限"
                    }
                }
            )
        
        return api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": f"获取API密钥详情失败: {str(e)}"
                }
            }
        )


@router.put("/{api_key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    api_key_id: str,
    api_key_data: ApiKeyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新API密钥"""
    try:
        api_key_service = ApiKeyService(db)
        
        # 检查权限
        api_key = api_key_service.get_api_key_by_id(api_key_id)
        if not api_key:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "API密钥不存在"
                    }
                }
            )
        
        if api_key.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": "没有访问权限"
                    }
                }
            )
        
        updated_api_key = api_key_service.update_api_key(api_key_id, api_key_data)
        return updated_api_key
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "UPDATE_FAILED",
                    "message": f"更新API密钥失败: {str(e)}"
                }
            }
        )


@router.delete("/{api_key_id}")
async def delete_api_key(
    api_key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除API密钥"""
    try:
        api_key_service = ApiKeyService(db)
        
        # 检查权限
        api_key = api_key_service.get_api_key_by_id(api_key_id)
        if not api_key:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "API密钥不存在"
                    }
                }
            )
        
        if api_key.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": "没有访问权限"
                    }
                }
            )
        
        api_key_service.delete_api_key(api_key_id)
        
        return {
            "success": True,
            "message": "API密钥删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "DELETE_FAILED",
                    "message": f"删除API密钥失败: {str(e)}"
                }
            }
        )


@router.get("/{api_key_id}/usage", response_model=ApiKeyUsageListResponse)
async def get_api_key_usage(
    api_key_id: str,
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取API密钥使用记录"""
    try:
        api_key_service = ApiKeyService(db)
        
        # 检查权限
        api_key = api_key_service.get_api_key_by_id(api_key_id)
        if not api_key:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "API密钥不存在"
                    }
                }
            )
        
        if api_key.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": "没有访问权限"
                    }
                }
            )
        
        usage_records = api_key_service.get_api_key_usage(api_key_id, days)
        
        return ApiKeyUsageListResponse(
            usage_records=usage_records,
            total=len(usage_records)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_USAGE_FAILED",
                    "message": f"获取使用记录失败: {str(e)}"
                }
            }
        )


@router.get("/{api_key_id}/quota", response_model=ApiKeyQuotaListResponse)
async def get_api_key_quota(
    api_key_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取API密钥配额信息"""
    try:
        api_key_service = ApiKeyService(db)
        
        # 检查权限
        api_key = api_key_service.get_api_key_by_id(api_key_id)
        if not api_key:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "API密钥不存在"
                    }
                }
            )
        
        if api_key.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": "没有访问权限"
                    }
                }
            )
        
        quotas = api_key_service.get_api_key_quota(api_key_id)
        
        return ApiKeyQuotaListResponse(quotas=quotas)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_QUOTA_FAILED",
                    "message": f"获取配额信息失败: {str(e)}"
                }
            }
        ) 