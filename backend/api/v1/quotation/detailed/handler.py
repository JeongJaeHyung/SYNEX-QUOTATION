# api/v1/quotation/detailed/handler.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from backend.database import get_db
from . import crud, schemas

handler = APIRouter()

# ============================================================
# Schema 생성 함수
# ============================================================

def get_detailed_resources_schema() -> dict:
    """DetailedResources 스키마 정의"""
    return {
        "machine_name": {
            "title": "장비명",
            "type": "string",
            "ratio": 2
        },
        "major": {
            "title": "대분류",
            "type": "string",
            "ratio": 2
        },
        "minor": {
            "title": "중분류",
            "type": "string",
            "ratio": 2
        },
        "unit": {
            "title": "단위",
            "type": "string",
            "ratio": 1
        },
        "solo_price": {
            "title": "단가",
            "type": "integer",
            "format": "currency",
            "ratio": 2
        },
        "compare": {
            "title": "수량",
            "type": "integer",
            "ratio": 1
        },
        "subtotal": {
            "title": "견적가",
            "type": "integer",
            "format": "currency",
            "ratio": 2
        },
        "description": {
            "title": "비고",
            "type": "string",
            "ratio": 2
        }
    }


# ============================================================
# Detailed Endpoints
# ============================================================

@handler.post("", status_code=201)
def create_detailed(
    detailed_data: schemas.DetailedCreate,
    db: Session = Depends(get_db)
):
    """
    Detailed 등록
    
    - general_id: 견적서(일반) ID (필수)
    - price_compare_id: 내정가견적비교서 ID (필수)
    - creator: 작성자 (필수)
    - description: 설명 (선택)
    
    자동 생성:
    - PriceCompareResources 데이터를 기반으로 DetailedResources 자동 생성
    """
    # Detailed 생성
    detailed = crud.create_detailed(
        db=db,
        general_id=detailed_data.general_id,
        price_compare_id=detailed_data.price_compare_id,
        creator=detailed_data.creator,
        description=detailed_data.description
    )
    
    # DetailedResources 조회
    resources = crud.get_detailed_resources(db, detailed.id)
    
    return {
        "detailed_id": detailed.id,
        "creator": detailed.creator,
        "description": detailed.description,
        "created_at": detailed.created_at,
        "detailed_resources": resources
    }


@handler.get("/{detailed_id}")
def get_detailed(
    detailed_id: UUID,
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    db: Session = Depends(get_db)
):
    """
    Detailed 조회
    
    - detailed_id: Detailed ID (UUID)
    - include_schema: true면 resources 스키마 포함
    """
    detailed = crud.get_detailed_by_id(db, detailed_id)
    if not detailed:
        raise HTTPException(status_code=404, detail="Detailed not found")
    
    # DetailedResources 조회
    resources = crud.get_detailed_resources(db, detailed_id)
    
    if include_schema:
        return {
            "id": detailed.id,
            "creator": detailed.creator,
            "description": detailed.description,
            "updated_at": detailed.updated_at,
            "resource_count": len(resources),
            "resources": {
                "schema": get_detailed_resources_schema(),
                "items": resources
            }
        }
    
    return {
        "id": detailed.id,
        "creator": detailed.creator,
        "description": detailed.description,
        "updated_at": detailed.updated_at,
        "resource_count": len(resources),
        "detailed_resources": resources
    }


@handler.put("/{detailed_id}")
def update_detailed(
    detailed_id: UUID,
    detailed_update: schemas.DetailedUpdate,
    db: Session = Depends(get_db)
):
    """
    Detailed 수정
    
    - detailed_id: Detailed ID (UUID)
    - creator: 작성자 (선택)
    - description: 설명 (선택)
    - detailed_resources: DetailedResources 전체 교체 (선택)
    """
    # resources 데이터 변환
    resources_data = None
    if detailed_update.detailed_resources:
        resources_data = [r.dict() for r in detailed_update.detailed_resources]
    
    # 수정
    updated_detailed = crud.update_detailed(
        db=db,
        detailed_id=detailed_id,
        creator=detailed_update.creator,
        description=detailed_update.description,
        detailed_resources=resources_data
    )
    
    if not updated_detailed:
        raise HTTPException(status_code=404, detail="Detailed not found")
    
    # DetailedResources 조회
    resources = crud.get_detailed_resources(db, detailed_id)
    
    return {
        "id": updated_detailed.id,
        "creator": updated_detailed.creator,
        "description": updated_detailed.description,
        "updated_at": updated_detailed.updated_at,
        "resource_count": len(resources),
        "detailed_resources": resources
    }


@handler.delete("/{detailed_id}")
def delete_detailed(
    detailed_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Detailed 삭제
    
    - detailed_id: Detailed ID (UUID)
    - CASCADE로 DetailedResources도 자동 삭제
    """
    success = crud.delete_detailed(db, detailed_id)
    if not success:
        raise HTTPException(status_code=404, detail="Detailed not found")
    
    return {
        "message": "Detailed deleted successfully",
        "deleted_id": str(detailed_id)
    }