from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# 💡 [추가] 연관 문서 아이템 정의 (테이블 행 데이터)
class RelatedDocumentItem(BaseModel):
    id: UUID
    category: str = Field(..., description="구분 (예: 비교견적, 상세견적)")
    title: str = Field(..., description="제목/비고 (표시용)")
    creator: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- General Create/Update ---
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

# --- General Response ---
class GeneralResponse(BaseModel):
    """General 응답"""
    id: UUID
    name: str
    client: Optional[str]
    creator: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # 💡 [추가] 연관된 문서 리스트 (기본값 빈 리스트)
    related_documents: List[RelatedDocumentItem] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)

# --- List Response (기존 유지) ---
class GeneralListItem(BaseModel):
    id: UUID
    name: str
    client: Optional[str]
    creator: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str]

class GeneralListResponse(BaseModel):
    total: int
    items: list[GeneralListItem]
    skip: int
    limit: int

class GeneralListWithSchemaResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    schema_data: dict = Field(..., alias="schema")
    total: int
    items: list[GeneralListItem]
    skip: int
    limit: int