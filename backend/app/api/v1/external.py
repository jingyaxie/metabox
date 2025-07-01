from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import time

from app.core.database import get_db
from app.core.auth import (
    validate_api_key, 
    record_api_usage,
    require_query_permission,
    require_search_permission,
    require_read_permission
)
from app.schemas.api_key import (
    ExternalQueryRequest,
    ExternalSearchRequest,
    ExternalHybridRequest,
    ExternalQueryResponse,
    ExternalSearchResponse,
    ExternalHybridResponse,
    ExternalKbInfoResponse,
    ExternalKbListResponse
)
from app.services.chat_service import ChatService
from app.services.retrieval_service import RetrievalService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.models.api_key import ApiKey
from .external_intelligent import router as external_intelligent_router

router = APIRouter(prefix="/api/v1", tags=["external"])

# 注册智能检索路由
router.include_router(external_intelligent_router)


@router.post("/chat/query", response_model=ExternalQueryResponse)
async def external_chat_query(
    request: ExternalQueryRequest,
    api_request: Request,
    api_key: ApiKey = Depends(require_query_permission()),
    db: Session = Depends(get_db)
):
    """外部API知识库问答接口"""
    start_time = time.time()
    
    try:
        # 检查知识库访问权限
        if request.kb_ids:
            for kb_id in request.kb_ids:
                if not api_key.has_permission("query", kb_id):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "success": False,
                            "error": {
                                "code": "KB_ACCESS_DENIED",
                                "message": f"没有访问知识库 {kb_id} 的权限"
                            }
                        }
                    )
        
        # 创建聊天服务
        chat_service = ChatService(db)
        
        # 处理流式响应
        if request.stream:
            async def generate_stream():
                try:
                    async for chunk in chat_service.stream_chat_response(
                        message=request.message,
                        kb_ids=request.kb_ids,
                        model_id=request.model_id,
                        session_id=request.session_id,
                        options=request.options or {}
                    ):
                        yield f"data: {json.dumps(chunk)}\n\n"
                    
                    # 记录使用情况
                    response_time = int((time.time() - start_time) * 1000)
                    await record_api_usage(
                        request=api_request,
                        api_key=api_key,
                        status_code=200,
                        tokens_used=0,  # 流式响应中难以准确计算
                        db=db
                    )
                    
                except Exception as e:
                    error_response = {
                        "success": False,
                        "error": {
                            "code": "STREAM_ERROR",
                            "message": str(e)
                        }
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        
        # 非流式响应
        response = await chat_service.chat_with_knowledge_base(
            message=request.message,
            kb_ids=request.kb_ids,
            model_id=request.model_id,
            session_id=request.session_id,
            options=request.options or {}
        )
        
        # 计算Token使用量
        tokens_used = response.get("usage", {}).get("total_tokens", 0)
        
        # 记录使用情况
        response_time = int((time.time() - start_time) * 1000)
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=200,
            tokens_used=tokens_used,
            db=db
        )
        
        return ExternalQueryResponse(
            success=True,
            data=response
        )
        
    except Exception as e:
        # 记录错误
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=500,
            tokens_used=0,
            db=db
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        )


@router.post("/retrieval/search", response_model=ExternalSearchResponse)
async def external_search(
    request: ExternalSearchRequest,
    api_request: Request,
    api_key: ApiKey = Depends(require_search_permission()),
    db: Session = Depends(get_db)
):
    """外部API向量检索接口"""
    start_time = time.time()
    
    try:
        # 检查知识库访问权限
        if request.kb_ids:
            for kb_id in request.kb_ids:
                if not api_key.has_permission("search", kb_id):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "success": False,
                            "error": {
                                "code": "KB_ACCESS_DENIED",
                                "message": f"没有访问知识库 {kb_id} 的权限"
                            }
                        }
                    )
        
        # 创建检索服务
        retrieval_service = RetrievalService(db)
        
        # 执行检索
        results = await retrieval_service.search_chunks(
            query=request.query,
            kb_ids=request.kb_ids,
            top_k=request.top_k or 10,
            similarity_threshold=request.similarity_threshold or 0.7,
            filters=request.filters or {}
        )
        
        # 记录使用情况
        response_time = int((time.time() - start_time) * 1000)
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=200,
            tokens_used=0,
            db=db
        )
        
        return ExternalSearchResponse(
            success=True,
            data={
                "results": results,
                "total": len(results),
                "query_time": response_time
            }
        )
        
    except Exception as e:
        # 记录错误
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=500,
            tokens_used=0,
            db=db
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        )


@router.post("/retrieval/hybrid", response_model=ExternalHybridResponse)
async def external_hybrid_search(
    request: ExternalHybridRequest,
    api_request: Request,
    api_key: ApiKey = Depends(require_search_permission()),
    db: Session = Depends(get_db)
):
    """外部API混合检索接口"""
    start_time = time.time()
    
    try:
        # 检查知识库访问权限
        if request.kb_ids:
            for kb_id in request.kb_ids:
                if not api_key.has_permission("search", kb_id):
                    raise HTTPException(
                        status_code=403,
                        detail={
                            "success": False,
                            "error": {
                                "code": "KB_ACCESS_DENIED",
                                "message": f"没有访问知识库 {kb_id} 的权限"
                            }
                        }
                    )
        
        # 创建检索服务
        retrieval_service = RetrievalService(db)
        
        # 执行混合检索
        results = await retrieval_service.hybrid_search(
            query=request.query,
            search_config=request.search_config,
            kb_ids=request.kb_ids,
            similarity_threshold=request.similarity_threshold or 0.7,
            filters=request.filters or {}
        )
        
        # 记录使用情况
        response_time = int((time.time() - start_time) * 1000)
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=200,
            tokens_used=0,
            db=db
        )
        
        return ExternalHybridResponse(
            success=True,
            data={
                "results": results,
                "total": len(results),
                "query_time": response_time
            }
        )
        
    except Exception as e:
        # 记录错误
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=500,
            tokens_used=0,
            db=db
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        )


@router.get("/kb/list", response_model=ExternalKbListResponse)
async def external_kb_list(
    api_request: Request,
    api_key: ApiKey = Depends(require_read_permission()),
    db: Session = Depends(get_db)
):
    """外部API获取知识库列表"""
    start_time = time.time()
    
    try:
        # 创建知识库服务
        kb_service = KnowledgeBaseService(db)
        
        # 获取用户可访问的知识库
        kb_ids = api_key.permissions.get("kb_ids", [])
        if kb_ids:
            # 如果指定了知识库ID列表，只返回这些知识库
            knowledge_bases = []
            for kb_id in kb_ids:
                kb = kb_service.get_knowledge_base(kb_id)
                if kb:
                    knowledge_bases.append(kb)
        else:
            # 如果没有指定，返回所有知识库（需要根据实际权限控制调整）
            knowledge_bases = kb_service.get_all_knowledge_bases()
        
        # 记录使用情况
        response_time = int((time.time() - start_time) * 1000)
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=200,
            tokens_used=0,
            db=db
        )
        
        return ExternalKbListResponse(
            success=True,
            data={
                "knowledge_bases": [
                    {
                        "id": kb.id,
                        "name": kb.name,
                        "description": kb.description,
                        "created_at": kb.created_at.isoformat(),
                        "document_count": kb.document_count,
                        "chunk_count": kb.chunk_count
                    }
                    for kb in knowledge_bases
                ],
                "total": len(knowledge_bases)
            }
        )
        
    except Exception as e:
        # 记录错误
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=500,
            tokens_used=0,
            db=db
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        )


@router.get("/kb/{kb_id}/info", response_model=ExternalKbInfoResponse)
async def external_kb_info(
    kb_id: str,
    api_request: Request,
    api_key: ApiKey = Depends(require_read_permission()),
    db: Session = Depends(get_db)
):
    """外部API获取知识库信息"""
    start_time = time.time()
    
    try:
        # 检查知识库访问权限
        if not api_key.has_permission("read", kb_id):
            raise HTTPException(
                status_code=403,
                detail={
                    "success": False,
                    "error": {
                        "code": "KB_ACCESS_DENIED",
                        "message": f"没有访问知识库 {kb_id} 的权限"
                    }
                }
            )
        
        # 创建知识库服务
        kb_service = KnowledgeBaseService(db)
        
        # 获取知识库信息
        kb = kb_service.get_knowledge_base(kb_id)
        if not kb:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "KB_NOT_FOUND",
                        "message": f"知识库 {kb_id} 不存在"
                    }
                }
            )
        
        # 记录使用情况
        response_time = int((time.time() - start_time) * 1000)
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=200,
            tokens_used=0,
            db=db
        )
        
        return ExternalKbInfoResponse(
            success=True,
            data={
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "created_at": kb.created_at.isoformat(),
                "updated_at": kb.updated_at.isoformat() if kb.updated_at else None,
                "document_count": kb.document_count,
                "chunk_count": kb.chunk_count,
                "embedding_model": kb.embedding_model,
                "chunk_size": kb.chunk_size,
                "chunk_overlap": kb.chunk_overlap
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # 记录错误
        await record_api_usage(
            request=api_request,
            api_key=api_key,
            status_code=500,
            tokens_used=0,
            db=db
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }
        ) 