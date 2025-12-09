# SYNEX+QUOTATION/Server/app/api/v1/quotation/machine/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ==================== Request Schemas ====================

class MachineResourceCreate(BaseModel):
    """Machine Resource 생성 요청"""
    maker_id: str = Field(..., min_length=1, max_length=4, description="제조사 ID")
    resources_id: str = Field(..., min_length=1, max_length=6, description="부품 ID")
    solo_price: int = Field(..., ge=0, description="단가 (견적 시점)")
    quantity: int = Field(..., ge=1, description="수량 (1 이상)")
    
    @field_validator('quantity')
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('quantity must be greater than or equal to 1')
        return v


class MachineCreate(BaseModel):
    """Machine 생성 요청"""
    name: str = Field(..., min_length=1, max_length=100, description="기계명")
    resources: List[MachineResourceCreate] = Field(..., min_items=1, description="구성 부품 목록")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "전광판제어기",
                "resources": [
                    {
                        "maker_id": "J012",
                        "resources_id": "000001",
                        "solo_price": 22000,
                        "quantity": 10
                    },
                    {
                        "maker_id": "J012",
                        "resources_id": "000002",
                        "solo_price": 3200000,
                        "quantity": 1
                    }
                ]
            }
        }


class MachineUpdate(BaseModel):
    """Machine 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="기계명")
    resources: Optional[List[MachineResourceCreate]] = Field(None, min_items=1, description="구성 부품 목록")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "전광판제어기 (수정)",
                "resources": [
                    {
                        "maker_id": "J012",
                        "resources_id": "000001",
                        "solo_price": 22000,
                        "quantity": 15
                    }
                ]
            }
        }


# ==================== Response Schemas ====================

class MakerInfo(BaseModel):
    """제조사 정보"""
    id: str
    name: str
    
    class Config:
        from_attributes = True


class CategoryInfo(BaseModel):
    """카테고리 정보"""
    id: int
    major: str
    minor: str
    
    class Config:
        from_attributes = True


class CertificationInfo(BaseModel):
    """인증 정보"""
    ul: bool
    ce: bool
    kc: bool
    etc: Optional[str] = None
    
    class Config:
        from_attributes = True


class MachineResourceResponse(BaseModel):
    """Machine Resource 응답 (상세 조회용)"""
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
    etc: Optional[str] = None
    solo_price: int
    quantity: int
    subtotal: int
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "maker_id": "J012",
                "resources_id": "000001",
                "model_name": "LCP-32FM 15A WA",
                "unit": "ea",
                "category_major": "잡재료 및 케이블",
                "category_minor": "열수축 튜브",
                "maker_name": "LS ELECTRIC",
                "ul": True,
                "ce": False,
                "kc": False,
                "etc": "RoHS",
                "solo_price": 22000,
                "quantity": 10,
                "subtotal": 220000
            }
        }


class MachineResponse(BaseModel):
    """Machine 상세 응답"""
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    total_price: int
    resource_count: int
    resources: List[MachineResourceResponse]
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "name": "전광판제어기",
                "created_at": "2024-12-08T16:45:59.108661",
                "updated_at": "2024-12-08T16:45:59.108661",
                "total_price": 3420000,
                "resource_count": 2,
                "resources": [
                    {
                        "maker_id": "J012",
                        "resources_id": "000001",
                        "model_name": "LCP-32FM 15A WA",
                        "unit": "ea",
                        "category_major": "잡재료 및 케이블",
                        "category_minor": "열수축 튜브",
                        "maker_name": "LS ELECTRIC",
                        "ul": True,
                        "ce": False,
                        "kc": False,
                        "etc": "RoHS",
                        "solo_price": 22000,
                        "quantity": 10,
                        "subtotal": 220000
                    }
                ]
            }
        }


class MachineListItem(BaseModel):
    """Machine 목록 항목 (간략 정보)"""
    id: UUID
    name: str
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                "name": "HMC 자세제 배터리 H2라 주유기(Filling)V-sealing(Unloader) 2라인 기능 전면 BOM",
                "updated_at": "2025-11-26T10:30:00"
            }
        }


class MachineListResponse(BaseModel):
    """Machine 목록 응답"""
    total: int
    items: List[MachineListItem]
    skip: int
    limit: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 50,
                "items": [
                    {
                        "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
                        "name": "HMC 자세제 배터리 H2라 주유기(Filling)V-sealing(Unloader) 2라인 기능 전면 BOM",
                        "updated_at": "2025-11-26T10:30:00"
                    }
                ],
                "skip": 0,
                "limit": 20
            }
        }