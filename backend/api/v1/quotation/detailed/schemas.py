# api/v1/quotation/detailed/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# ============================================================
# DetailedResources Schemas
# ============================================================

class DetailedResourceItem(BaseModel):
    """DetailedResources 항목"""
    machine_name: str = Field(..., max_length=100, description="장비명")
    major: str = Field(..., max_length=30, description="대분류")
    minor: str = Field(..., max_length=50, description="중분류")
    unit: str = Field(..., max_length=10, description="단위")
    solo_price: int = Field(..., ge=0, description="단가")
    compare: int = Field(..., ge=0, description="수량")
    description: Optional[str] = Field(None, description="비고")


class DetailedResourceResponse(BaseModel):
    """DetailedResources 응답 (subtotal 포함)"""
    machine_name: str
    major: str
    minor: str
    unit: str
    solo_price: int
    compare: int
    subtotal: int
    description: Optional[str]


# ============================================================
# Detailed Schemas
# ============================================================

class DetailedCreate(BaseModel):
    """Detailed 생성 요청"""
    general_id: UUID = Field(..., description="견적서(일반) ID")
    price_compare_id: UUID = Field(..., description="내정가견적비교서 ID")
    creator: str = Field(..., max_length=25, description="작성자")
    description: Optional[str] = Field(None, description="설명")


class DetailedUpdate(BaseModel):
    """Detailed 수정 요청 (선택적)"""
    creator: Optional[str] = Field(None, max_length=25, description="작성자")
    description: Optional[str] = Field(None, description="설명")
    detailed_resources: Optional[List[DetailedResourceItem]] = Field(None, description="DetailedResources 전체 교체")


class DetailedResponse(BaseModel):
    """Detailed 응답"""
    id: UUID
    creator: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class DetailedCreateResponse(BaseModel):
    """Detailed 생성 응답"""
    detailed_id: UUID
    creator: str
    description: Optional[str]
    created_at: datetime
    detailed_resources: List[DetailedResourceResponse]


class DetailedDetailResponse(BaseModel):
    """Detailed 상세 응답 (without schema)"""
    id: UUID
    creator: str
    description: Optional[str]
    updated_at: datetime
    resource_count: int
    detailed_resources: List[DetailedResourceResponse]


class DetailedDetailWithSchemaResponse(BaseModel):
    """Detailed 상세 응답 (with schema)"""
    model_config = ConfigDict(protected_namespaces=())
    
    id: UUID
    creator: str
    description: Optional[str]
    updated_at: datetime
    resource_count: int
    resources: dict  # {"schema": {...}, "items": [...]}