from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RecallTestBase(BaseModel):
    name: str = Field(..., description="测试名称")
    description: Optional[str] = Field(None, description="测试描述")
    test_type: str = Field(default="manual", description="测试类型")
    config: Dict[str, Any] = Field(default_factory=dict, description="测试配置")

class RecallTestCreate(RecallTestBase):
    knowledge_base_id: str = Field(..., description="知识库ID")

class RecallTestUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class RecallTestResponse(RecallTestBase):
    id: str
    knowledge_base_id: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_queries: int = 0
    total_relevant: int = 0
    total_retrieved: int = 0
    total_correct: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    avg_response_time: float = 0.0

class RecallTestCaseBase(BaseModel):
    query: str = Field(..., description="测试查询")
    expected_chunks: List[str] = Field(default_factory=list, description="期望返回的chunk IDs")
    expected_images: List[str] = Field(default_factory=list, description="期望返回的image IDs")
    relevance_score: float = Field(default=1.0, description="相关性评分")
    category: Optional[str] = Field(None, description="查询类别")

class RecallTestCaseCreate(RecallTestCaseBase):
    pass

class RecallTestCaseUpdate(BaseModel):
    query: Optional[str] = None
    expected_chunks: Optional[List[str]] = None
    expected_images: Optional[List[str]] = None
    relevance_score: Optional[float] = None
    category: Optional[str] = None

class RecallTestCaseResponse(RecallTestCaseBase):
    id: str
    recall_test_id: str
    created_at: datetime
    retrieved_chunks: List[str] = Field(default_factory=list)
    retrieved_images: List[str] = Field(default_factory=list)
    response_time: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    is_correct: bool = False

class RecallTestRunRequest(BaseModel):
    test_id: str
    config: Optional[Dict[str, Any]] = None

class RecallTestResult(BaseModel):
    test_id: str
    status: str
    total_queries: int
    total_relevant: int
    total_retrieved: int
    total_correct: int
    precision: float
    recall: float
    f1_score: float
    avg_response_time: float
    completed_at: datetime

class RecallTestReport(BaseModel):
    test: RecallTestResponse
    test_cases: List[RecallTestCaseResponse]
    summary: Dict[str, Any]
    charts: Dict[str, Any]

class BatchTestCaseImport(BaseModel):
    test_cases: List[RecallTestCaseCreate] 