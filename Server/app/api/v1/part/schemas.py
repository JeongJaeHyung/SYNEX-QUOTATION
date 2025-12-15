# api/v1/parts/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class PartsFilter(BaseModel):
    """Parts 필터링용 스키마"""
    id: Optional[str] = None
    maker_id: Optional[str] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    major: Optional[str] = None
    minor: Optional[str] = None
    ul: Optional[bool] = None
    ce: Optional[bool] = None
    kc: Optional[bool] = None


class PartsCreate(BaseModel):
    """Parts 생성용 스키마"""
    maker_name: str
    major_category: str
    minor_category: str
    name: str
    unit: str
    solo_price: int
    display_order: Optional[int] = None
    ul: Optional[bool] = False
    ce: Optional[bool] = False
    kc: Optional[bool] = False
    certification_etc: Optional[str] = None


class PartsUpdate(BaseModel):
    """Parts 수정용 스키마"""
    major_category: Optional[str] = None
    minor_category: Optional[str] = None
    name: Optional[str] = None
    unit: Optional[str] = None
    solo_price: Optional[int] = None
    ul: Optional[bool] = None
    ce: Optional[bool] = None
    kc: Optional[bool] = None
    certification_etc: Optional[str] = None


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
    etc: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PartsSearchRequest(BaseModel):
    """Parts 검색 요청 스키마"""
    query: str
    search_fields: List[str]
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
    items: List[PartsResponse]
    skip: int
    limit: int
