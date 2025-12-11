# api/v1/parts/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

# ============================================================
# Parts Schemas
# ============================================================

class PartsCreate(BaseModel):
    """Parts 등록 요청"""
    maker_name: str = Field(..., max_length=100)
    major_category: str = Field(..., max_length=50)
    minor_category: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    unit: str = Field(..., max_length=10)
    solo_price: int = Field(..., ge=0)
    ul: bool = Field(default=False)
    ce: bool = Field(default=False)
    kc: bool = Field(default=False)
    etc: Optional[str] = None

class PartsUpdate(BaseModel):
    """Parts 수정 요청 (선택적)"""
    major_category: Optional[str] = Field(None, max_length=50)
    minor_category: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    unit: Optional[str] = Field(None, max_length=10)
    solo_price: Optional[int] = Field(None, ge=0)
    ul: Optional[bool] = None
    ce: Optional[bool] = None
    kc: Optional[bool] = None
    etc: Optional[str] = None

class PartsFilter(BaseModel):
    """Parts 필터 (CRUD용)"""
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

class PartsSearch(BaseModel):
    """Parts 검색 요청"""
    query: str = Field(..., min_length=1)
    search_fields: List[str] = Field(..., min_items=1)
    include_schema: bool = Field(default=False)
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)

class PartsItem(BaseModel):
    """Parts 항목"""
    item_code: str
    id: str
    maker_id: str
    maker_name: str
    category_id: int
    major_category: str
    minor_category: str
    name: str
    unit: str
    solo_price: int
    ul: bool
    ce: bool
    kc: bool
    etc: Optional[str]

class PartsDetailResponse(BaseModel):
    """Parts 단일 조회 응답 (schema 없음)"""
    item_code: str
    id: str
    maker_id: str
    maker_name: str
    major_category: str
    minor_category: str
    name: str
    unit: str
    solo_price: int
    ul: bool
    ce: bool
    kc: bool
    etc: Optional[str]

class PartsDetailWithSchemaResponse(BaseModel):
    """Parts 단일 조회 응답 (schema 있음)"""
    model_config = ConfigDict(protected_namespaces=())  # schema 필드 경고 해결
    
    schema_data: dict = Field(..., alias="schema")  # schema → schema_data
    item: PartsDetailResponse

class PartsListResponse(BaseModel):
    """Parts 목록 조회 응답 (schema 없음)"""
    total: int
    items: List[PartsItem]
    skip: int
    limit: int

class PartsListWithSchemaResponse(BaseModel):
    """Parts 목록 조회 응답 (schema 있음)"""
    model_config = ConfigDict(protected_namespaces=())  # schema 필드 경고 해결
    
    schema_data: dict = Field(..., alias="schema")  # schema → schema_data
    total: int
    items: List[PartsItem]
    skip: int
    limit: int

class PartsCreateResponse(BaseModel):
    """Parts 등록 응답"""
    item_code: str
    id: str
    maker_id: str
    maker_name: str
    category_id: int
    major_category: str
    minor_category: str
    name: str
    unit: str
    solo_price: int
    ul: bool
    ce: bool
    kc: bool
    etc: Optional[str]
    created_at: datetime

class PartsUpdateResponse(BaseModel):
    """Parts 수정 응답"""
    item_code: str
    id: str
    maker_id: str
    maker_name: str
    category_id: int
    major_category: str
    minor_category: str
    name: str
    unit: str
    solo_price: int
    ul: bool
    ce: bool
    kc: bool
    etc: Optional[str]
    updated_at: datetime

class PartsDeleteResponse(BaseModel):
    """Parts 삭제 응답"""
    message: str
    deleted_item_code: str