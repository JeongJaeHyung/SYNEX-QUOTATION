# api/v1/quotation/header/schemas.py
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================
# HeaderResources Schemas
# ============================================================


class HeaderResourceItem(BaseModel):
    """HeaderResources 항목"""

    machine: str = Field(..., max_length=100, description="장비명")
    name: str = Field(..., max_length=100, description="품명")
    spac: str | None = Field(None, max_length=50, description="규격")
    compare: int = Field(..., ge=0, description="수량")
    unit: str = Field(..., max_length=10, description="단위")
    solo_price: int = Field(..., ge=0, description="단가")
    description: str | None = Field(None, description="비고")


class HeaderResourceResponse(BaseModel):
    """HeaderResources 응답 (subtotal 포함)"""

    machine: str
    name: str
    spac: str | None
    compare: int
    unit: str
    solo_price: int
    subtotal: int
    description: str | None


# ============================================================
# Header Schemas
# ============================================================


class HeaderCreate(BaseModel):
    """Header 생성 요청"""

    folder_id: UUID = Field(..., description="폴더 id")
    detailed_id: UUID = Field(..., description="을지 ID")
    title: str = Field(..., max_length=100, description="갑지 제목")
    creator: str = Field(..., max_length=25, description="작성자")
    client: str = Field(..., max_length=50, description="고객사")
    manufacturer: str | None = Field(None, max_length=50, description="장비사")
    pic_name: str = Field(..., max_length=50, description="고객사 담당자명")
    pic_position: str = Field(..., max_length=50, description="고객사 담당자 직급")


class HeaderUpdate(BaseModel):
    """Header 수정 요청 (선택적)"""

    title: str | None = Field(None, max_length=100, description="갑지 제목")
    creator: str | None = Field(None, max_length=25, description="작성자")
    client: str | None = Field(None, max_length=50, description="고객사")
    manufacturer: str | None = Field(None, max_length=50, description="장비사")
    pic_name: str | None = Field(None, max_length=50, description="고객사 담당자명")
    pic_position: str | None = Field(
        None, max_length=50, description="고객사 담당자 직급"
    )
    description_1: str | None = Field(None, description="설명1")
    description_2: str | None = Field(None, description="설명2")
    header_resources: list[HeaderResourceItem] | None = Field(
        None, description="HeaderResources 전체 교체"
    )


class HeaderResponse(BaseModel):
    """Header 기본 응답"""

    id: UUID
    title: str
    price: int | None
    creator: str
    client: str | None
    manufacturer: str | None
    pic_name: str | None
    pic_position: str | None
    description_1: str | None
    description_2: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HeaderCreateResponse(BaseModel):
    """Header 생성 응답"""

    id: UUID
    title: str
    price: int | None
    creator: str
    client: str | None
    manufacturer: str | None
    pic_name: str | None
    pic_position: str | None
    description_1: str | None
    description_2: str | None
    updated_at: datetime
    resource_count: int
    header_resources: list[HeaderResourceResponse]


class HeaderDetailResponse(BaseModel):
    """Header 상세 응답 (without schema)"""

    id: UUID
    title: str
    price: int | None
    creator: str
    client: str | None
    manufacturer: str | None
    pic_name: str | None
    pic_position: str | None
    description_1: str | None
    description_2: str | None
    updated_at: datetime
    resource_count: int
    header_resources: list[HeaderResourceResponse]


class HeaderDetailWithSchemaResponse(BaseModel):
    """Header 상세 응답 (with schema)"""

    model_config = ConfigDict(protected_namespaces=())

    id: UUID
    title: str
    price: int | None
    creator: str
    client: str | None
    manufacturer: str | None
    pic_name: str | None
    pic_position: str | None
    description_1: str | None
    description_2: str | None
    updated_at: datetime
    resource_count: int
    resources: dict  # {"schema": {...}, "items": [...]}
