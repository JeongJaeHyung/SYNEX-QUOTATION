# api/v1/quotation/machine/handler.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from database import get_db
from api.v1.quotation.machine import schemas, crud

handler = APIRouter()

# ============================================================
# Schema 생성 함수
# ============================================================

def get_machine_list_schema() -> dict:
    """Machine 목록 조회 Schema"""
    return {
        "name": {
            "title": "장비명",
            "type": "string",
            "ratio": 5
        },
        "creator": {
            "title": "작성자",
            "type": "string",
            "ratio": 1
        },
        "updated_at": {
            "title": "최종수정일",
            "type": "datetime",
            "format": "YYYY-MM-DD HH:mm",
            "ratio": 2
        },
        "description": {
            "title": "비고",
            "type": "string",
            "ratio": 5
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
            "title": "제조사",
            "type": "string",
            "ratio": 2
        },
        "category_major": {
            "title": "대분류",
            "type": "string",
            "ratio": 2
        },
        "category_minor": {
            "title": "중분류",
            "type": "string",
            "ratio": 2
        },
        "model_name": {
            "title": "모델명",
            "type": "string",
            "ratio": 3
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
        "quantity": {
            "title": "수량",
            "type": "integer",
            "ratio": 1
        },
        "subtotal": {
            "title": "소계",
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
    
    - name: 장비명 (필수)
    - creator: 작성자명 (필수)
    - description: 비고 (선택)
    - resources: 구성 부품 목록 (필수)
    """
    # Resources 존재 확인 생략 (CRUD에서 FK 제약조건으로 처리)
    
    # Machine 생성
    resources_data = [r.dict() for r in machine.resources]
    db_machine = crud.create_machine(
        db=db,
        name=machine.name,
        creator=machine.creator,
        description=machine.description,
        resources=resources_data
    )
    
    # Resources 상세 정보 조회
    resources_detail = crud.get_machine_resources_detail(db, db_machine.id)
    
    # 총액 계산
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    return {
        "id": db_machine.id,
        "name": db_machine.name,
        "creator": db_machine.creator,
        "description": db_machine.description,
        "created_at": db_machine.created_at,
        "total_price": total_price,
        "resource_count": len(resources_detail),
        "resources": resources_detail
    }


@handler.get("/", response_model=schemas.MachineListResponse)
def get_machines(
    include_schema: bool = Query(False, description="schema 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Machine 목록 조회 (updated_at DESC)
    
    - include_schema: true면 schema 포함
    - skip: 건너뛸 개수
    - limit: 가져올 개수
    """
    total, machines = crud.get_machines(db, skip=skip, limit=limit)
    
    items = [
        {
            "id": m.id,
            "name": m.name,
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


@handler.get("/search", response_model=schemas.MachineListResponse)
def search_machines(
    search: str = Query(..., min_length=1, description="검색어"),
    include_schema: bool = Query(False, description="schema 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Machine 검색 (name 부분 매칭)
    
    - search: 검색어 (필수)
    - include_schema: true면 schema 포함
    - skip: 건너뛸 개수
    - limit: 가져올 개수
    """
    total, machines = crud.search_machines(db, search=search, skip=skip, limit=limit)
    
    items = [
        {
            "id": m.id,
            "name": m.name,
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
    
    - machine_id: Machine ID (UUID)
    - include_schema: true면 resources에 schema 포함
    """
    machine = crud.get_machine_by_id(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Resources 상세 정보
    resources_detail = crud.get_machine_resources_detail(db, machine_id)
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    if include_schema:
        return {
            "id": machine.id,
            "name": machine.name,
            "creator": machine.creator,
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
        "creator": machine.creator,
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
    
    - name: 장비명 (선택)
    - description: 비고 (선택)
    - resources: 구성 부품 목록 (선택)
    """
    # Resources 데이터 변환
    resources_data = None
    if machine_update.resources:
        resources_data = [r.dict() for r in machine_update.resources]
    
    # 수정
    updated_machine = crud.update_machine(
        db=db,
        machine_id=machine_id,
        name=machine_update.name,
        description=machine_update.description,
        resources=resources_data
    )
    
    if not updated_machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    
    # Resources 상세 정보
    resources_detail = crud.get_machine_resources_detail(db, machine_id)
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    return {
        "id": updated_machine.id,
        "name": updated_machine.name,
        "creator": updated_machine.creator,
        "description": updated_machine.description,
        "updated_at": updated_machine.updated_at,
        "total_price": total_price,
        "resource_count": len(resources_detail),
        "resources": resources_detail
    }