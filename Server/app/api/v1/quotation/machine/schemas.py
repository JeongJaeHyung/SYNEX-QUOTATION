# api/v1/quotation/machine/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID

# ============================================================
# Machine Resource Schemas
# ============================================================

class MachineResourceCreate(BaseModel):
    """Machine 구성 부품"""
    maker_id: str = Field(..., max_length=4)
    resources_id: str = Field(..., max_length=6)
    solo_price: int = Field(..., ge=0)
    quantity: int = Field(..., ge=1)

class MachineResourceDetail(BaseModel):
    """Machine 구성 부품 상세"""
    item_code: str
    maker_id: str
    resources_id: str
    model_name: str
    unit: str
    category_major: str
    category_minor: str
    maker_name: str
    ul: bool
    ce: bool
    kc: bool
    etc: Optional[str]
    solo_price: int
    quantity: int
    subtotal: int

# ============================================================
# Machine Schemas
# ============================================================

class MachineCreate(BaseModel):
    """Machine 등록 요청"""
    name: str = Field(..., max_length=100)
    creator: str = Field(..., max_length=10)
    description: Optional[str] = Field(None, max_length=500)
    resources: List[MachineResourceCreate]

class MachineUpdate(BaseModel):
    """Machine 수정 요청 (선택적)"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    resources: Optional[List[MachineResourceCreate]] = None

class MachineListItem(BaseModel):
    """Machine 목록 항목"""
    id: UUID
    name: str
    creator: str
    description: Optional[str]
    updated_at: datetime

class MachineListResponse(BaseModel):
    """Machine 목록 조회 응답 (schema 없음)"""
    total: int
    items: List[MachineListItem]
    skip: int
    limit: int

class MachineListWithSchemaResponse(BaseModel):
    """Machine 목록 조회 응답 (schema 있음)"""
    model_config = ConfigDict(protected_namespaces=())  # schema 필드 경고 해결
    
    schema_data: dict = Field(..., alias="schema")
    total: int
    items: List[MachineListItem]
    skip: int
    limit: int

class MachineResourcesWithSchemaResponse(BaseModel):
    """Machine 리소스 응답 (schema 있음)"""
    model_config = ConfigDict(protected_namespaces=())  # schema 필드 경고 해결
    
    schema_data: dict = Field(..., alias="schema")
    items: List[MachineResourceDetail]

class MachineResourcesResponse(BaseModel):
    """Machine 리소스 응답 (schema 없음)"""
    items: List[MachineResourceDetail]

class MachineDetailResponse(BaseModel):
    """Machine 상세 조회 응답"""
    id: UUID
    name: str
    creator: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    total_price: int
    resource_count: int
    resources: dict  # schema 포함 여부에 따라 구조 다름

class MachineCreateResponse(BaseModel):
    """Machine 등록 응답"""
    id: UUID
    name: str
    creator: str
    description: Optional[str]
    created_at: datetime
    total_price: int
    resource_count: int
    resources: List[MachineResourceDetail]

class MachineUpdateResponse(BaseModel):
    """Machine 수정 응답"""
    id: UUID
    name: str
    creator: str
    description: Optional[str]
    updated_at: datetime
    total_price: int
    resource_count: int
    resources: List[MachineResourceDetail]