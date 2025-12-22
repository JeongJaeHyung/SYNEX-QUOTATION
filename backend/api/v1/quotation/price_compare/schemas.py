# SYNEX+QUOTATION/backend/api/v1/quotation/price_compare/schemas.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# --- Resources Schema ---
class ResourceItem(BaseModel):
    # [중요] 리소스 식별용 장비 ID (PK) 💡
    machine_id: UUID = Field(..., description="장비 ID (PK)")
    # 장비명 필드 추가 (비고가 아닌 별도 필드)
    machine_name: Optional[str] = Field(None, description="장비명")
    
    major: str = Field(..., max_length=30, description="대분류 (PK)")
    minor: str = Field(..., max_length=50, description="중분류 (PK)")
    
    cost_solo_price: int = Field(..., description="내정 단가")
    cost_unit: str = Field(..., max_length=10, description="내정 단위")
    cost_compare: int = Field(..., description="내정 수량")
    
    quotation_solo_price: int = Field(..., description="견적 단가")
    quotation_unit: str = Field(..., max_length=10, description="견적 단위")
    quotation_compare: int = Field(..., description="견적 수량")
    
    upper: float = Field(..., description="상승 반영율(%)")
    description: Optional[str] = Field(None, description="비고 (자동계산 시 장비명)")

    model_config = ConfigDict(from_attributes=True)

# --- Create Request ---
class PriceCompareCreate(BaseModel):
    general_id: UUID
    creator: str = Field(..., max_length=25)
    description: Optional[str] = None
    machine_ids: List[UUID] = Field(..., description="연결할 장비 ID 목록")

# --- Update Request ---
class PriceCompareUpdate(BaseModel):
    creator: str = Field(..., max_length=25)
    description: Optional[str] = None
    machine_ids: List[UUID] = Field(..., description="연결할 장비 ID 목록")
    
    # Optional로 설정하여, 값을 안 보내면(None) 자동 재계산 로직이 돌도록 함 💡
    price_compare_resources: Optional[List[ResourceItem]] = Field(None)

# --- Response ---
class PriceCompareResponse(BaseModel):
    id: UUID
    general_id: UUID
    creator: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    price_compare_resources: List[ResourceItem] = Field(default_factory=list)
    
    # 응답 시 편의성을 위해 ID 리스트만 반환
    machine_ids: List[UUID] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
