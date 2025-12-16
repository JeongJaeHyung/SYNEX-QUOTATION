# app/api/v1/quotation/general/handler.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from . import crud, schemas

handler = APIRouter()

# ============================================================
# Schema 생성 함수
# ============================================================

def get_general_schema() -> dict:
    """General 스키마 정의 (사용자용)"""
    return {
        "name": {
            "title": "견적서명",
            "type": "string",
            "ratio": 3
        },
        "client": {
            "title": "고객사",
            "type": "string",
            "ratio": 2
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
            "ratio": 3
        }
    }


def get_general_relations_schema() -> dict:
    """General 연관 테이블 스키마 정의"""
    return {
        "table_name": {
            "title": "구분",
            "type": "string",
            "ratio": 2
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
            "ratio": 4
        }
    }


# ============================================================
# General Endpoints
# ============================================================

@handler.post("", status_code=201)
def create_general(
    general_data: schemas.GeneralCreate,
    db: Session = Depends(get_db)
):
    """
    General 생성
    
    - name: 견적서명 (필수)
    - client: 고객사 (선택)
    - creator: 작성자 (필수)
    - description: 비고 (선택)
    """
    general = crud.create_general(
        db=db,
        name=general_data.name,
        client=general_data.client,
        creator=general_data.creator,
        description=general_data.description
    )
    
    return {
        "id": general.id,
        "name": general.name,
        "client": general.client,
        "creator": general.creator,
        "description": general.description,
        "created_at": general.created_at,
        "message": "General created successfully"
    }


@handler.get("")
def get_generals(
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    General 목록 조회 (전체)
    
    - include_schema: true면 schema 포함
    - skip: 건너뛸 개수
    - limit: 가져올 개수
    
    응답: id, name, client, creator, created_at, updated_at, description
    사용자 표시용: name, client, creator, updated_at, description (id, created_at 제외)
    """
    total, generals = crud.get_generals(db, skip=skip, limit=limit)
    
    # 전체 데이터 (id, created_at 포함)
    items = [
        {
            "id": g.id,
            "name": g.name,
            "client": g.client,
            "creator": g.creator,
            "created_at": g.created_at,
            "updated_at": g.updated_at,
            "description": g.description
        }
        for g in generals
    ]
    
    if include_schema:
        return {
            "schema": get_general_schema(),  # id, created_at 제외된 스키마
            "total": total,
            "items": items,  # 전체 데이터 (id, created_at 포함)
            "skip": skip,
            "limit": limit
        }
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }


@handler.get("/{general_id}")
def get_general(
    general_id: UUID,
    include_relations: bool = Query(False, description="연관 테이블 포함 여부"),
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    db: Session = Depends(get_db)
):
    """
    General 단일 조회
    
    - general_id: General ID (UUID)
    - include_relations: true면 PriceCompare, Detailed, Quotation 목록 포함
    - include_schema: true면 연관 테이블 스키마 포함
    
    반환 필드: table_name(구분), id, creator, updated_at, description
    사용자 표시: table_name, creator, updated_at, description (id 제외)
    """
    if include_relations:
        # 연관 테이블 포함
        result = crud.get_general_with_relations(db, general_id)
        if not result:
            raise HTTPException(status_code=404, detail="General not found")
        
        if include_schema:
            result["schema"] = get_general_relations_schema()
        
        return result
    else:
        # 기본 정보만
        general = crud.get_general_by_id(db, general_id)
        if not general:
            raise HTTPException(status_code=404, detail="General not found")
        
        return {
            "id": general.id,
            "name": general.name,
            "client": general.client,
            "creator": general.creator,
            "description": general.description,
            "created_at": general.created_at,
            "updated_at": general.updated_at
        }


@handler.put("/{general_id}")
def update_general(
    general_id: UUID,
    general_update: schemas.GeneralUpdate,
    db: Session = Depends(get_db)
):
    """
    General 수정 (부분 수정)
    
    - general_id: General ID (UUID)
    - name, client, creator, description 중 수정할 항목만 전송
    """
    updated_general = crud.update_general(
        db=db,
        general_id=general_id,
        name=general_update.name,
        client=general_update.client,
        creator=general_update.creator,
        description=general_update.description
    )
    
    if not updated_general:
        raise HTTPException(status_code=404, detail="General not found")
    
    return {
        "id": updated_general.id,
        "name": updated_general.name,
        "client": updated_general.client,
        "creator": updated_general.creator,
        "description": updated_general.description,
        "updated_at": updated_general.updated_at,
        "message": "General updated successfully"
    }


@handler.delete("/{general_id}")
def delete_general(
    general_id: UUID,
    db: Session = Depends(get_db)
):
    """
    General 삭제
    
    - general_id: General ID (UUID)
    - CASCADE로 연관된 Quotation, Detailed, PriceCompare도 자동 삭제
    """
    success = crud.delete_general(db, general_id)
    if not success:
        raise HTTPException(status_code=404, detail="General not found")
    
    return {
        "message": "General deleted successfully",
        "deleted_id": str(general_id)
    }