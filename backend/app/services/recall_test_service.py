from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from app.models.recall_test import RecallTest, RecallTestCase
from app.models.knowledge_base import KnowledgeBase, KnowledgeBaseChunk as TextChunk, KnowledgeBaseImage as ImageVector
from app.schemas.recall_test import (
    RecallTestCreate, RecallTestUpdate, RecallTestCaseCreate, RecallTestCaseUpdate, BatchTestCaseImport, RecallTestRunRequest
)
from datetime import datetime
import time

class RecallTestService:
    def __init__(self, db: Session):
        self.db = db

    # 召回测试管理
    def list_tests(self, kb_id: str, user_id: str) -> List[RecallTest]:
        self._check_kb_permission(kb_id, user_id)
        return self.db.query(RecallTest).filter(RecallTest.knowledge_base_id == kb_id).all()

    def create_test(self, kb_id: str, data: RecallTestCreate, user_id: str) -> RecallTest:
        self._check_kb_permission(kb_id, user_id)
        test = RecallTest(
            knowledge_base_id=kb_id,
            name=data.name,
            description=data.description,
            test_type=data.test_type,
            config=data.config,
            status="draft"
        )
        self.db.add(test)
        self.db.commit()
        self.db.refresh(test)
        return test

    def get_test(self, kb_id: str, test_id: str, user_id: str) -> RecallTest:
        self._check_kb_permission(kb_id, user_id)
        test = self.db.query(RecallTest).filter(RecallTest.id == test_id, RecallTest.knowledge_base_id == kb_id).first()
        if not test:
            raise HTTPException(status_code=404, detail="召回测试不存在")
        return test

    def update_test(self, kb_id: str, test_id: str, data: RecallTestUpdate, user_id: str) -> RecallTest:
        test = self.get_test(kb_id, test_id, user_id)
        if data.name:
            test.name = data.name
        if data.description:
            test.description = data.description
        if data.config:
            test.config = data.config
        test.updated_at = datetime.utcnow()
        self.db.commit()
        return test

    def delete_test(self, kb_id: str, test_id: str, user_id: str):
        test = self.get_test(kb_id, test_id, user_id)
        self.db.delete(test)
        self.db.commit()

    # 用例管理
    def list_cases(self, kb_id: str, test_id: str, user_id: str) -> List[RecallTestCase]:
        self.get_test(kb_id, test_id, user_id)
        return self.db.query(RecallTestCase).filter(RecallTestCase.recall_test_id == test_id).all()

    def create_case(self, kb_id: str, test_id: str, data: RecallTestCaseCreate, user_id: str) -> RecallTestCase:
        self.get_test(kb_id, test_id, user_id)
        case = RecallTestCase(
            recall_test_id=test_id,
            query=data.query,
            expected_chunks=data.expected_chunks,
            expected_images=data.expected_images,
            relevance_score=data.relevance_score,
            category=data.category
        )
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def batch_import_cases(self, kb_id: str, test_id: str, data: BatchTestCaseImport, user_id: str) -> List[RecallTestCase]:
        self.get_test(kb_id, test_id, user_id)
        cases = []
        for item in data.test_cases:
            case = RecallTestCase(
                recall_test_id=test_id,
                query=item.query,
                expected_chunks=item.expected_chunks,
                expected_images=item.expected_images,
                relevance_score=item.relevance_score,
                category=item.category
            )
            self.db.add(case)
            cases.append(case)
        self.db.commit()
        return cases

    def update_case(self, kb_id: str, test_id: str, case_id: str, data: RecallTestCaseUpdate, user_id: str) -> RecallTestCase:
        self.get_test(kb_id, test_id, user_id)
        case = self.db.query(RecallTestCase).filter(RecallTestCase.id == case_id, RecallTestCase.recall_test_id == test_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        if data.query:
            case.query = data.query
        if data.expected_chunks is not None:
            case.expected_chunks = data.expected_chunks
        if data.expected_images is not None:
            case.expected_images = data.expected_images
        if data.relevance_score is not None:
            case.relevance_score = data.relevance_score
        if data.category is not None:
            case.category = data.category
        self.db.commit()
        return case

    def delete_case(self, kb_id: str, test_id: str, case_id: str, user_id: str):
        self.get_test(kb_id, test_id, user_id)
        case = self.db.query(RecallTestCase).filter(RecallTestCase.id == case_id, RecallTestCase.recall_test_id == test_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="测试用例不存在")
        self.db.delete(case)
        self.db.commit()

    # 运行测试
    async def run_test(self, kb_id: str, test_id: str, data: RecallTestRunRequest, user_id: str):
        test = self.get_test(kb_id, test_id, user_id)
        cases = self.db.query(RecallTestCase).filter(RecallTestCase.recall_test_id == test_id).all()
        total_queries = len(cases)
        total_relevant = 0
        total_retrieved = 0
        total_correct = 0
        total_response_time = 0.0
        for case in cases:
            start = time.time()
            # 简单模拟检索（实际应调用RAG服务）
            retrieved_chunks = self._simple_recall(case.query, kb_id)
            response_time = (time.time() - start) * 1000
            case.retrieved_chunks = [c.id for c in retrieved_chunks]
            case.response_time = response_time
            # 计算指标
            expected_set = set(case.expected_chunks)
            retrieved_set = set(case.retrieved_chunks)
            correct = expected_set & retrieved_set
            precision = len(correct) / len(retrieved_set) if retrieved_set else 0.0
            recall = len(correct) / len(expected_set) if expected_set else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
            case.precision = precision
            case.recall = recall
            case.f1_score = f1
            case.is_correct = recall > 0
            total_relevant += len(expected_set)
            total_retrieved += len(retrieved_set)
            total_correct += len(correct)
            total_response_time += response_time
        # 汇总
        test.total_queries = total_queries
        test.total_relevant = total_relevant
        test.total_retrieved = total_retrieved
        test.total_correct = total_correct
        test.precision = total_correct / total_retrieved if total_retrieved else 0.0
        test.recall = total_correct / total_relevant if total_relevant else 0.0
        test.f1_score = 2 * test.precision * test.recall / (test.precision + test.recall) if (test.precision + test.recall) else 0.0
        test.avg_response_time = total_response_time / total_queries if total_queries else 0.0
        test.status = "completed"
        self.db.commit()
        # 构造报告
        return self.get_report(kb_id, test_id, user_id)

    def get_report(self, kb_id: str, test_id: str, user_id: str):
        test = self.get_test(kb_id, test_id, user_id)
        cases = self.db.query(RecallTestCase).filter(RecallTestCase.recall_test_id == test_id).all()
        # 简单图表数据
        charts = {
            "precision": [c.precision for c in cases],
            "recall": [c.recall for c in cases],
            "f1": [c.f1_score for c in cases],
            "response_time": [c.response_time for c in cases],
        }
        summary = {
            "total_queries": test.total_queries,
            "total_relevant": test.total_relevant,
            "total_retrieved": test.total_retrieved,
            "total_correct": test.total_correct,
            "precision": test.precision,
            "recall": test.recall,
            "f1_score": test.f1_score,
            "avg_response_time": test.avg_response_time
        }
        return {
            "test": test,
            "test_cases": cases,
            "summary": summary,
            "charts": charts
        }

    def _check_kb_permission(self, kb_id: str, user_id: str):
        kb = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()
        if not kb or kb.owner_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问知识库")

    def _simple_recall(self, query: str, kb_id: str):
        # 简单关键词检索模拟
        chunks = self.db.query(TextChunk).filter(TextChunk.knowledge_base_id == kb_id).all()
        query_words = query.lower().split()
        relevant = []
        for chunk in chunks:
            content_lower = chunk.content.lower()
            if any(word in content_lower for word in query_words):
                relevant.append(chunk)
        return relevant[:5]  # 取前5个 