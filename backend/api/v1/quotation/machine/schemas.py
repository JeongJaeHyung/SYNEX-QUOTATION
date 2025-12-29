# api/v1/quotation/machine/schemas.py
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# ============================================================
# Machine Resource Schemas
# ============================================================


class MachineResourceCreate(BaseModel):
    """Machine 구성 부품"""

    maker_id: str = Field(..., max_length=4)
    resources_id: str = Field(..., max_length=6)
    solo_price: int = Field(..., ge=0)
    quantity: int = Field(..., ge=0)
    display_major: str | None = Field(None, max_length=50)
    display_minor: str | None = Field(None, max_length=50)
    display_model_name: str | None = Field(None, max_length=100)
    display_maker_name: str | None = Field(None, max_length=100)
    display_unit: str | None = Field(None, max_length=10)


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
    etc: str | None
    solo_price: int
    quantity: int
    subtotal: int


# ============================================================
# Machine Schemas
# ============================================================


class MachineCreate(BaseModel):
    """Machine 등록 요청"""

    name: str = Field(..., max_length=100)
    manufacturer: str | None = Field(None, max_length=50)  # ✅ 추가
    client: str | None = Field(None, max_length=50)  # ✅ 추가
    creator: str = Field(..., max_length=25)
    description: str | None = Field(None, max_length=500)
    resources: list[MachineResourceCreate]


class MachineUpdate(BaseModel):
    """Machine 수정 요청 (선택적)"""

    name: str | None = Field(None, max_length=100)
    manufacturer: str | None = Field(None, max_length=50)  # ✅ 추가
    client: str | None = Field(None, max_length=50)  # ✅ 추가
    description: str | None = Field(None, max_length=500)
    resources: list[MachineResourceCreate] | None = None


class MachineListItem(BaseModel):
    """Machine 목록 항목"""

    id: UUID
    name: str
    manufacturer: str | None  # ✅ 추가
    client: str | None  # ✅ 추가
    creator: str
    description: str | None
    updated_at: datetime


class MachineListResponse(BaseModel):
    """Machine 목록 조회 응답 (schema 없음)"""

    total: int
    items: list[MachineListItem]
    skip: int
    limit: int


class MachineListWithSchemaResponse(BaseModel):
    """Machine 목록 조회 응답 (schema 있음)"""

    model_config = ConfigDict(protected_namespaces=())

    schema_data: dict = Field(..., alias="schema")
    total: int
    items: list[MachineListItem]
    skip: int
    limit: int


class MachineResourcesWithSchemaResponse(BaseModel):
    """Machine 리소스 응답 (schema 있음)"""

    model_config = ConfigDict(protected_namespaces=())

    schema_data: dict = Field(..., alias="schema")
    items: list[MachineResourceDetail]


class MachineDetailResponse(BaseModel):
    """Machine 상세 조회 응답"""

    id: UUID
    name: str
    manufacturer: str | None  # ✅ 추가
    client: str | None  # ✅ 추가
    creator: str
    price: int | None  # ✅ 추가 (총액)
    description: str | None
    created_at: datetime
    updated_at: datetime
    total_price: int
    resource_count: int
    resources: list[MachineResourceDetail] | dict

    model_config = ConfigDict(from_attributes=True)


class MachineCreateResponse(BaseModel):
    """Machine 등록 응답"""

    id: UUID
    name: str
    manufacturer: str | None  # ✅ 추가
    client: str | None  # ✅ 추가
    creator: str
    description: str | None
    created_at: datetime
    total_price: int
    resource_count: int
    resources: list[MachineResourceDetail]


class MachineUpdateResponse(BaseModel):
    """Machine 수정 응답"""

    id: UUID
    name: str
    manufacturer: str | None  # ✅ 추가
    client: str | None  # ✅ 추가
    creator: str
    description: str | None
    updated_at: datetime
    total_price: int
    resource_count: int
    resources: list[MachineResourceDetail]
