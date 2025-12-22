# api/v1/quotation/header/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# ============================================================
# HeaderResources Schemas
# ============================================================

class HeaderResourceItem(BaseModel):
    """HeaderResources 항목"""
    machine: str = Field(..., max_length=100, description="장비명")
    name: str = Field(..., max_length=100, description="품명")
    spac: Optional[str] = Field(None, max_length=50, description="규격")
    compare: int = Field(..., ge=0, description="수량")
    unit: str = Field(..., max_length=10, description="단위")
    solo_price: int = Field(..., ge=0, description="단가")
    description: Optional[str] = Field(None, description="비고")


class HeaderResourceResponse(BaseModel):
    """HeaderResources 응답 (subtotal 포함)"""
    machine: str
    name: str
    spac: Optional[str]
    compare: int
    unit: str
    solo_price: int
    subtotal: int
    description: Optional[str]


# ============================================================
# Header Schemas
# ============================================================

class HeaderCreate(BaseModel):
    """Header 생성 요청"""
    general_id: UUID = Field(..., description="견적서(일반) ID")
    detailed_id: UUID = Field(..., description="을지 ID")
    title: str = Field(..., max_length=100, description="갑지 제목")
    creator: str = Field(..., max_length=25, description="작성자")
    client: str = Field(..., max_length=50, description="고객사")
    pic_name: str = Field(..., max_length=50, description="고객사 담당자명")
    pic_position: str = Field(..., max_length=50, description="고객사 담당자 직급")


class HeaderUpdate(BaseModel):
    """Header 수정 요청 (선택적)"""
    title: Optional[str] = Field(None, max_length=100, description="갑지 제목")
    creator: Optional[str] = Field(None, max_length=25, description="작성자")
    client: Optional[str] = Field(None, max_length=50, description="고객사")
    pic_name: Optional[str] = Field(None, max_length=50, description="고객사 담당자명")
    pic_position: Optional[str] = Field(None, max_length=50, description="고객사 담당자 직급")
    description_1: Optional[str] = Field(None, description="설명1")
    description_2: Optional[str] = Field(None, description="설명2")
    header_resources: Optional[List[HeaderResourceItem]] = Field(None, description="HeaderResources 전체 교체")


class HeaderResponse(BaseModel):
    """Header 기본 응답"""
    id: UUID
    title: str
    price: Optional[int]
    creator: str
    client: Optional[str]
    pic_name: Optional[str]
    pic_position: Optional[str]
    description_1: Optional[str]
    description_2: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class HeaderCreateResponse(BaseModel):
    """Header 생성 응답"""
    quotation_id: UUID
    title: str
    price: Optional[int]
    creator: str
    client: Optional[str]
    pic_name: Optional[str]
    pic_position: Optional[str]
    description_1: Optional[str]
    description_2: Optional[str]
    updated_at: datetime
    resource_count: int
    header_resources: List[HeaderResourceResponse]


class HeaderDetailResponse(BaseModel):
    """Header 상세 응답 (without schema)"""
    quotation_id: UUID
    title: str
    price: Optional[int]
    creator: str
    client: Optional[str]
    pic_name: Optional[str]
    pic_position: Optional[str]
    description_1: Optional[str]
    description_2: Optional[str]
    updated_at: datetime
    resource_count: int
    header_resources: List[HeaderResourceResponse]


class HeaderDetailWithSchemaResponse(BaseModel):
    """Header 상세 응답 (with schema)"""
    model_config = ConfigDict(protected_namespaces=())
    
    quotation_id: UUID
    title: str
    price: Optional[int]
    creator: str
    client: Optional[str]
    pic_name: Optional[str]
    pic_position: Optional[str]
    description_1: Optional[str]
    description_2: Optional[str]
    updated_at: datetime
    resource_count: int
    resources: dict  # {"schema": {...}, "items": [...]}