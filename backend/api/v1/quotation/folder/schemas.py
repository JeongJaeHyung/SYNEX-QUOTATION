from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# --- Folder Resource Item (Header, Detailed, PriceCompare) ---
class FolderResourceItem(BaseModel):
    """Folder에 속한 리소스 아이템"""

    table_name: str = Field(..., description="유형 (내정가 비교, 견적서(을지), 견적서)")
    id: UUID
    title: str
    creator: str
    updated_at: datetime
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


# --- Folder Create ---
class FolderCreate(BaseModel):
    """Folder 생성 요청"""

    general_id: UUID = Field(..., description="견적서(일반) id")
    title: str = Field(..., max_length=100, description="제목")


# --- Folder Update ---
class FolderUpdate(BaseModel):
    """Folder 수정 요청"""

    title: str | None = Field(None, max_length=100, description="제목")


# --- Folder Response ---
class FolderResponse(BaseModel):
    """Folder 응답 (기본)"""

    id: UUID
    title: str
    updated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Folder Response with Resources ---
class FolderResponseWithResources(BaseModel):
    """Folder 응답 (리소스 포함)"""

    id: UUID
    title: str
    updated_at: datetime
    resource_count: int
    resources: list[FolderResourceItem] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
