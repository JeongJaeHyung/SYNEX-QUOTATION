# api/v1/maker/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MakerCreate(BaseModel):
    """Maker 생성 요청"""
    id: Optional[str] = Field(None, max_length=4, description="제조사코드 (선택, 없으면 자동생성)")
    name: str = Field(..., max_length=100, description="제조사명")

class MakerUpdate(BaseModel):
    """Maker 수정 요청"""
    name: str = Field(..., max_length=100, description="제조사명")

class MakerResponse(BaseModel):
    """Maker 응답"""
    id: str
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None