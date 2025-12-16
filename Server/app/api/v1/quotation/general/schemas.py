# api/v1/general/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class GeneralCreate(BaseModel):
    """General 생성 요청"""
    name: str = Field(..., max_length=100, description="견적서명")
    client: Optional[str] = Field(None, max_length=50, description="고객사")
    creator: str = Field(..., max_length=25, description="작성자")
    description: Optional[str] = Field(None, description="비고")


class GeneralUpdate(BaseModel):
    """General 수정 요청 (선택적)"""
    name: Optional[str] = Field(None, max_length=100, description="견적서명")
    client: Optional[str] = Field(None, max_length=50, description="고객사")
    creator: Optional[str] = Field(None, max_length=25, description="작성자")
    description: Optional[str] = Field(None, description="비고")


class GeneralResponse(BaseModel):
    """General 응답"""
    id: UUID
    name: str
    client: Optional[str]
    creator: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GeneralListItem(BaseModel):
    """General 목록 항목 (전체 데이터)"""
    id: UUID
    name: str
    client: Optional[str]
    creator: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str]


class GeneralListResponse(BaseModel):
    """General 목록 응답 (schema 없음)"""
    total: int
    items: list[GeneralListItem]
    skip: int
    limit: int


class GeneralListWithSchemaResponse(BaseModel):
    """General 목록 응답 (schema 있음)"""
    model_config = ConfigDict(protected_namespaces=())
    
    schema_data: dict = Field(..., alias="schema")
    total: int
    items: list[GeneralListItem]
    skip: int
    limit: int#