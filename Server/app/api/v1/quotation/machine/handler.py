# api/v1/quotation/machine/handler.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, Union
from uuid import UUID
from database import get_db
from api.v1.quotation.machine import schemas, crud
from models.resources import Resources  # ✅ 추가

handler = APIRouter()

# ============================================================
# Schema 생성 함수 (변경 없음)
# ============================================================

def get_machine_list_schema() -> dict:
    """Machine 목록 조회 Schema"""
    return {
        "name": {
            "title": "장비명",
            "type": "string",
            "ratio": 4,
            "align": "left"
        },
        "manufacturer": {
            "title": "장비사",  # 또는 "Maker" - 원하는 대로 선택
            "type": "string",
            "ratio": 2,
            "align": "center"
        },
        "client": {
            "title": "고객사",
            "type": "string",
            "ratio": 2,
            "align": "center"
        },
        "creator": {
            "title": "작성자",
            "type": "string",
            "ratio": 1,
            "align": "center"
        },
        "updated_at": {
            "title": "최종수정일",
            "type": "datetime",
            "format": "YYYY-MM-DD HH:mm",
            "ratio": 2,
            "align": "center"
        },
        "description": {
            "title": "비고",
            "type": "string",
            "ratio": 3,
            "align": "left"
        }
    }

def get_machine_resources_schema() -> dict:
    """Machine Resources Schema"""
    return {
        "item_code": {
            "title": "품목코드",
            "type": "string",
            "ratio": 2
        },
        "maker_name": {
            "title": "Maker",  # ✅ 변경
            "type": "string",
            "ratio": 2
        },
        "category_major": {
            "title": "Unit",  # ✅ 변경
            "type": "string",
            "ratio": 2
        },
        "category_minor": {
            "title": "품목",  # ✅ 변경
            "type": "string",
            "ratio": 2
        },
        "model_name": {
            "title": "모델명/규격",  # ✅ 변경
            "type": "string",
            "ratio": 3
        },
        "unit": {
            "title": "단위",
            "type": "string",
            "ratio": 1
        },
        "solo_price": {
            "title": "금액",  # ✅ 변경
            "type": "integer",
            "format": "currency",
            "ratio": 2
        },
        "quantity": {
            "title": "수량",
            "type": "integer",
            "ratio": 1
        },
        "subtotal": {
            "title": "합계 금액",  # ✅ 변경
            "type": "integer",
            "format": "currency",
            "ratio": 2
        }
    }

# ============================================================
# Machine Endpoints
# ============================================================

@handler.post("/", response_model=schemas.MachineCreateResponse, status_code=201)
def register_machine(
    machine: schemas.MachineCreate,
    db: Session = Depends(get_db)
):
    """
    Machine 등록
    
    Resources 처리:
    - maker_id가 일반 제조사: Resources 테이블에 존재하는지 검증
    - maker_id="SUMMARY": 집계 항목 (검증 스킵)
    - maker_id="LABOR": 인건비 항목 (검증 스킵)
    """
    # ========== 실제 부품 검증 ==========
    for resource in machine.resources:
        # SUMMARY, LABOR는 검증 스킵
        if resource.maker_id in ["SUMMARY", "LABOR"]:
            continue
        
        # 실제 부품 존재 여부 확인
        existing_resource = db.query(Resources).filter(
            Resources.maker_id == resource.maker_id,
            Resources.id == resource.resources_id
        ).first()
        
        if not existing_resource:
            raise HTTPException(
                status_code=404,
                detail=f"Resource not found: {resource.maker_id}-{resource.resources_id}"
            )
    
    # ========== Machine 생성 ==========
    resources_data = [r.dict() for r in machine.resources]
    db_machine = crud.create_machine(
        db=db,
        name=machine.name,
        manufacturer=machine.manufacturer,
        client=machine.client,
        creator=machine.creator,
        description=machine.description,
        resources=resources_data
    )
    
    # ========== Resources 상세 정보 조회 ==========
    resources_detail = crud.get_machine_resources_detail(db, db_machine.id)
    
    # 총액 계산
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    return {
        "id": db_machine.id,
        "name": db_machine.name,
        "manufacturer": db_machine.manufacturer,
        "client": db_machine.client,
        "creator": db_machine.creator,
        "description": db_machine.description,
        "created_at": db_machine.created_at,
        "total_price": total_price,
        "resource_count": len(resources_detail),
        "resources": resources_detail
    }


@handler.get("/", response_model=Union[schemas.MachineListWithSchemaResponse, schemas.MachineListResponse])
def get_machines(
    include_schema: bool = Query(False, description="schema 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Machine 목록 조회 (updated_at DESC)
    """
    total, machines = crud.get_machines(db, skip=skip, limit=limit)
    
    items = [
        {
            "id": m.id,
            "name": m.name,
            "manufacturer": m.manufacturer,
            "client": m.client,
            "creator": m.creator,
            "description": m.description,
            "updated_at": m.updated_at
        }
        for m in machines
    ]
    
    if include_schema:
        return {
            "schema": get_machine_list_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }


@handler.get("/search", response_model=Union[schemas.MachineListWithSchemaResponse, schemas.MachineListResponse])
def search_machines(
    search: str = Query(..., min_length=1, description="검색어"),
    include_schema: bool = Query(False, description="schema 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Machine 검색 (name 부분 매칭)
    """
    total, machines = crud.search_machines(db, search=search, skip=skip, limit=limit)
    
    items = [
        {
            "id": m.id,
            "name": m.name,
            "manufacturer": m.manufacturer,
            "client": m.client,
            "creator": m.creator,
            "description": m.description,
            "updated_at": m.updated_at
        }
        for m in machines
    ]
    
    if include_schema:
        return {
            "schema": get_machine_list_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }


@handler.get("/{machine_id}", response_model=schemas.MachineDetailResponse)
def get_machine(
    machine_id: UUID,
    include_schema: bool = Query(False, description="schema 포함 여부"),
    db: Session = Depends(get_db)
):
    """
    Machine 상세 조회
    """
    machine = crud.get_machine_by_id(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Resources 상세 정보 (SUMMARY/LABOR 포함)
    resources_detail = crud.get_machine_resources_detail(db, machine_id)
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    if include_schema:
        return {
            "id": machine.id,
            "name": machine.name,
            "manufacturer": machine.manufacturer,
            "client": machine.client,
            "creator": machine.creator,
            "price": machine.price,
            "description": machine.description,
            "created_at": machine.created_at,
            "updated_at": machine.updated_at,
            "total_price": total_price,
            "resource_count": len(resources_detail),
            "resources": {
                "schema": get_machine_resources_schema(),
                "items": resources_detail
            }
        }
    
    return {
        "id": machine.id,
        "name": machine.name,
        "manufacturer": machine.manufacturer,
        "client": machine.client,
        "creator": machine.creator,
        "price": machine.price,
        "description": machine.description,
        "created_at": machine.created_at,
        "updated_at": machine.updated_at,
        "total_price": total_price,
        "resource_count": len(resources_detail),
        "resources": resources_detail
    }


@handler.put("/{machine_id}", response_model=schemas.MachineUpdateResponse)
def update_machine(
    machine_id: UUID,
    machine_update: schemas.MachineUpdate,
    db: Session = Depends(get_db)
):
    """
    Machine 수정
    """
    # ========== 실제 부품 검증 ==========
    if machine_update.resources:
        for resource in machine_update.resources:
            # SUMMARY, LABOR는 검증 스킵
            if resource.maker_id in ["SUMMARY", "LABOR"]:
                continue
            
            # 실제 부품 존재 여부 확인
            existing_resource = db.query(Resources).filter(
                Resources.maker_id == resource.maker_id,
                Resources.id == resource.resources_id
            ).first()
            
            if not existing_resource:
                raise HTTPException(
                    status_code=404,
                    detail=f"Resource not found: {resource.maker_id}-{resource.resources_id}"
                )
    
    # ========== Resources 데이터 변환 ==========
    resources_data = None
    if machine_update.resources:
        resources_data = [r.dict() for r in machine_update.resources]
    
    # ========== 수정 ==========
    updated_machine = crud.update_machine(
        db=db,
        machine_id=machine_id,
        name=machine_update.name,
        manufacturer=machine_update.manufacturer,
        client=machine_update.client,
        description=machine_update.description,
        resources=resources_data
    )
    
    if not updated_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # ========== Resources 상세 정보 ==========
    resources_detail = crud.get_machine_resources_detail(db, machine_id)
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    return {
        "id": updated_machine.id,
        "name": updated_machine.name,
        "manufacturer": updated_machine.manufacturer,
        "client": updated_machine.client,
        "creator": updated_machine.creator,
        "description": updated_machine.description,
        "updated_at": updated_machine.updated_at,
        "total_price": total_price,
        "resource_count": len(resources_detail),
        "resources": resources_detail
    }