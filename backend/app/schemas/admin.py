from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class ProviderType(str, Enum):
    LLM = "llm"
    EMBEDDING = "embedding"
    VISION = "vision"

class ModelType(str, Enum):
    TEXT = "text"
    VISION = "vision"
    EMBEDDING = "embedding"

class SuperAdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: EmailStr

class SuperAdminLogin(BaseModel):
    username: str
    password: str

class SuperAdminResponse(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

class ModelProviderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    provider_type: ProviderType
    api_base_url: Optional[str] = None
    api_key: str = Field(..., min_length=1)
    config: Optional[Dict[str, Any]] = None

class ModelProviderUpdate(BaseModel):
    display_name: Optional[str] = None
    api_base_url: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class ModelProviderResponse(BaseModel):
    id: str
    name: str
    display_name: str
    provider_type: ProviderType
    api_base_url: Optional[str]
    is_active: bool
    config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

class ModelConfigCreate(BaseModel):
    provider_id: str
    model_name: str = Field(..., min_length=1, max_length=100)
    display_name: str = Field(..., min_length=1, max_length=100)
    model_type: ModelType
    max_tokens: Optional[int] = None
    temperature: Optional[str] = "0.7"
    is_default: bool = False
    config: Optional[Dict[str, Any]] = None

class ModelConfigUpdate(BaseModel):
    display_name: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None

class ModelConfigResponse(BaseModel):
    id: str
    provider_id: str
    model_name: str
    display_name: str
    model_type: ModelType
    max_tokens: Optional[int]
    temperature: Optional[str]
    is_default: bool
    is_active: bool
    config: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    provider: ModelProviderResponse

class SystemConfigCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: str = "general"
    is_encrypted: bool = False

class SystemConfigUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_encrypted: Optional[bool] = None

class SystemConfigResponse(BaseModel):
    id: str
    key: str
    value: str
    description: Optional[str]
    category: str
    is_encrypted: bool
    created_at: datetime
    updated_at: Optional[datetime]

class ModelProviderWithModels(BaseModel):
    provider: ModelProviderResponse
    models: List[ModelConfigResponse]

class AdminDashboardStats(BaseModel):
    total_providers: int
    active_providers: int
    total_models: int
    active_models: int
    total_configs: int
    system_status: Dict[str, Any] 