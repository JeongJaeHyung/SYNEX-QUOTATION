# api/v1/maker/handler.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from . import crud, schemas

handler = APIRouter()

# ============================================================
# Schema 생성 함수
# ============================================================

def get_maker_schema() -> dict:
    """Maker 스키마 정의"""
    return {
        "id": {
            "title": "제조사코드",
            "type": "string",
            "ratio": 1
        },
        "name": {
            "title": "제조사명",
            "type": "string",
            "ratio": 3
        },
        "created_at": {
            "title": "등록일",
            "type": "datetime",
            "format": "YYYY-MM-DD HH:mm",
            "ratio": 2
        }
    }


# ============================================================
# Maker Endpoints
# ============================================================

@handler.post("", status_code=201)
def create_maker(
    maker_data: schemas.MakerCreate,
    db: Session = Depends(get_db)
):
    """
    Maker 등록
    
    - id: 제조사코드 (선택, 없으면 자동생성 M001, M002...)
    - name: 제조사명 (필수)
    """
    # 이름 중복 체크
    existing = crud.get_maker_by_name(db, maker_data.name)
    if existing:
        raise HTTPException(status_code=409, detail=f"Maker '{maker_data.name}' already exists")
    
    # ID 중복 체크 (ID가 제공된 경우)
    if maker_data.id:
        existing_id = crud.get_maker_by_id(db, maker_data.id)
        if existing_id:
            raise HTTPException(status_code=409, detail=f"Maker ID '{maker_data.id}' already exists")
    
    # Maker 생성
    maker = crud.create_maker(db, maker_data.id, maker_data.name)
    
    return {
        "id": maker.id,
        "name": maker.name,
        "created_at": maker.created_at,
        "message": "Maker created successfully"
    }


@handler.get("")
def get_makers(
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Maker 목록 조회
    
    - include_schema: true면 schema 포함
    - skip: 건너뛸 개수
    - limit: 가져올 개수
    """
    total, makers = crud.get_makers(db, skip=skip, limit=limit)
    
    items = [
        {
            "id": m.id,
            "name": m.name,
            "created_at": m.created_at
        }
        for m in makers
    ]
    
    if include_schema:
        return {
            "schema": get_maker_schema(),
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


@handler.get("/search")
def search_makers(
    query: str = Query(..., min_length=1, description="검색어"),
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Maker 검색 (name 부분 매칭)
    
    - query: 검색어 (필수)
    - include_schema: true면 schema 포함
    """
    total, makers = crud.search_makers(db, query, skip=skip, limit=limit)
    
    items = [
        {
            "id": m.id,
            "name": m.name,
            "created_at": m.created_at
        }
        for m in makers
    ]
    
    if include_schema:
        return {
            "schema": get_maker_schema(),
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


@handler.get("/{maker_id}")
def get_maker(
    maker_id: str,
    db: Session = Depends(get_db)
):
    """
    Maker 상세 조회
    
    - maker_id: 제조사코드
    """
    maker = crud.get_maker_by_id(db, maker_id)
    if not maker:
        raise HTTPException(status_code=404, detail="Maker not found")
    
    return {
        "id": maker.id,
        "name": maker.name,
        "created_at": maker.created_at,
        "updated_at": maker.updated_at
    }


@handler.put("/{maker_id}")
def update_maker(
    maker_id: str,
    maker_update: schemas.MakerUpdate,
    db: Session = Depends(get_db)
):
    """
    Maker 수정
    
    - maker_id: 제조사코드
    - name: 새 제조사명
    """
    updated_maker = crud.update_maker(db, maker_id, maker_update.name)
    if not updated_maker:
        raise HTTPException(status_code=404, detail="Maker not found")
    
    return {
        "id": updated_maker.id,
        "name": updated_maker.name,
        "updated_at": updated_maker.updated_at,
        "message": "Maker updated successfully"
    }


@handler.delete("/{maker_id}")
def delete_maker(
    maker_id: str,
    db: Session = Depends(get_db)
):
    """
    Maker 삭제
    
    - maker_id: 제조사코드
    """
    success = crud.delete_maker(db, maker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Maker not found")
    
    return {
        "message": "Maker deleted successfully",
        "deleted_id": maker_id
    }