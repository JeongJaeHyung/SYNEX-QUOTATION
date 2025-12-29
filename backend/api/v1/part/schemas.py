# api/v1/parts/schemas.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PartsFilter(BaseModel):
    """Parts 필터링용 스키마"""

    id: str | None = None
    maker_id: str | None = None
    name: str | None = None
    unit: str | None = None
    min_price: int | None = None
    max_price: int | None = None
    major: str | None = None
    minor: str | None = None
    ul: bool | None = None
    ce: bool | None = None
    kc: bool | None = None


class PartsCreate(BaseModel):
    """Parts 생성용 스키마"""

    maker_name: str
    major_category: str
    minor_category: str
    name: str
    unit: str
    solo_price: int
    display_order: int | None = None
    ul: bool | None = False
    ce: bool | None = False
    kc: bool | None = False
    certification_etc: str | None = None


class PartsUpdate(BaseModel):
    """Parts 수정용 스키마"""

    major_category: str | None = None
    minor_category: str | None = None
    name: str | None = None
    unit: str | None = None
    solo_price: int | None = None
    ul: bool | None = None
    ce: bool | None = None
    kc: bool | None = None
    certification_etc: str | None = None


class PartsResponse(BaseModel):
    """Parts 응답용 스키마"""

    item_code: str
    id: str
    maker_id: str
    maker_name: str
    major_category: str  # ✅ category_id 제거
    minor_category: str  # ✅ category_id 제거
    name: str
    unit: str
    solo_price: int
    ul: bool
    ce: bool
    kc: bool
    etc: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PartsSearchRequest(BaseModel):
    """Parts 검색 요청 스키마"""

    query: str
    search_fields: list[str]
    include_schema: bool = False
    skip: int = 0
    limit: int = 20


class PartsDetailWithSchemaResponse(BaseModel):
    """Parts 상세 + Schema 응답"""

    model_config = ConfigDict(protected_namespaces=())

    schema_data: dict = Field(..., alias="schema")
    item: PartsResponse


class PartsListWithSchemaResponse(BaseModel):
    """Parts 목록 + Schema 응답"""

    model_config = ConfigDict(protected_namespaces=())

    schema_data: dict = Field(..., alias="schema")
    total: int
    items: list[PartsResponse]
    skip: int
    limit: int
