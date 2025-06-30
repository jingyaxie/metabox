"""
召回测试 API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.auth_service import AuthService
from app.services.recall_test_service import RecallTestService
from app.schemas.recall_test import (
    RecallTestCreate, RecallTestUpdate, RecallTestResponse,
    RecallTestCaseCreate, RecallTestCaseUpdate, RecallTestCaseResponse,
    RecallTestRunRequest, RecallTestReport, BatchTestCaseImport
)

router = APIRouter()
security = HTTPBearer()

# 召回测试管理
@router.get("/kb/{kb_id}/recall-tests/", response_model=List[RecallTestResponse])
async def list_recall_tests(
    kb_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.list_tests(kb_id, user.id)

@router.post("/kb/{kb_id}/recall-tests/", response_model=RecallTestResponse)
async def create_recall_test(
    kb_id: str,
    data: RecallTestCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.create_test(kb_id, data, user.id)

@router.get("/kb/{kb_id}/recall-tests/{test_id}", response_model=RecallTestResponse)
async def get_recall_test(
    kb_id: str,
    test_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.get_test(kb_id, test_id, user.id)

@router.put("/kb/{kb_id}/recall-tests/{test_id}", response_model=RecallTestResponse)
async def update_recall_test(
    kb_id: str,
    test_id: str,
    data: RecallTestUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.update_test(kb_id, test_id, data, user.id)

@router.delete("/kb/{kb_id}/recall-tests/{test_id}")
async def delete_recall_test(
    kb_id: str,
    test_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    recall_service.delete_test(kb_id, test_id, user.id)
    return {"message": "删除成功"}

# 用例管理
@router.get("/kb/{kb_id}/recall-tests/{test_id}/cases", response_model=List[RecallTestCaseResponse])
async def list_test_cases(
    kb_id: str,
    test_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.list_cases(kb_id, test_id, user.id)

@router.post("/kb/{kb_id}/recall-tests/{test_id}/cases", response_model=RecallTestCaseResponse)
async def create_test_case(
    kb_id: str,
    test_id: str,
    data: RecallTestCaseCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.create_case(kb_id, test_id, data, user.id)

@router.post("/kb/{kb_id}/recall-tests/{test_id}/cases/batch", response_model=List[RecallTestCaseResponse])
async def batch_import_cases(
    kb_id: str,
    test_id: str,
    data: BatchTestCaseImport,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.batch_import_cases(kb_id, test_id, data, user.id)

@router.put("/kb/{kb_id}/recall-tests/{test_id}/cases/{case_id}", response_model=RecallTestCaseResponse)
async def update_test_case(
    kb_id: str,
    test_id: str,
    case_id: str,
    data: RecallTestCaseUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.update_case(kb_id, test_id, case_id, data, user.id)

@router.delete("/kb/{kb_id}/recall-tests/{test_id}/cases/{case_id}")
async def delete_test_case(
    kb_id: str,
    test_id: str,
    case_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    recall_service.delete_case(kb_id, test_id, case_id, user.id)
    return {"message": "删除成功"}

# 运行测试
@router.post("/kb/{kb_id}/recall-tests/{test_id}/run", response_model=RecallTestReport)
async def run_recall_test(
    kb_id: str,
    test_id: str,
    data: RecallTestRunRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return await recall_service.run_test(kb_id, test_id, data, user.id)

# 获取报告
@router.get("/kb/{kb_id}/recall-tests/{test_id}/report", response_model=RecallTestReport)
async def get_recall_test_report(
    kb_id: str,
    test_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    recall_service = RecallTestService(db)
    user = auth_service.get_current_user(credentials.credentials)
    return recall_service.get_report(kb_id, test_id, user.id) 