# api/v1/parts/handler.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from . import schemas, crud

handler = APIRouter()

# ============================================================
# Schema 생성 함수
# ============================================================

def get_parts_schema() -> dict:
    """Parts Schema"""
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
        "major_category": {
            "title": "대분류",
            "type": "string",
            "ratio": 2
        },
        "minor_category": {
            "title": "중분류",
            "type": "string",
            "ratio": 2
        },
        "name": {
            "title": "부품명",
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
        "ul": {
            "title": "UL",
            "type": "boolean",
            "ratio": 1
        },
        "ce": {
            "title": "CE",
            "type": "boolean",
            "ratio": 1
        },
        "kc": {
            "title": "KC",
            "type": "boolean",
            "ratio": 1
        },
        "etc": {
            "title": "기타인증",
            "type": "string",
            "ratio": 2
        }
    }

# ============================================================
# Parts Endpoints
# ============================================================

@handler.post("/", response_model=schemas.PartsCreateResponse, status_code=201)
def register_parts(
    parts: schemas.PartsCreate,
    db: Session = Depends(get_db)
):
    """
    Parts 등록
    
    - maker_name으로 maker_id 자동 조회
    - major_category + minor_category로 category_id 자동 조회
    - id는 제조사별 자동 증가
    """
    # Maker 조회
    maker = crud.get_maker_by_name(db, parts.maker_name)
    if not maker:
        raise HTTPException(status_code=404, detail=f"Maker '{parts.maker_name}' not found")
    
    # Category 조회
    category = crud.get_category_by_major_minor(db, parts.major_category, parts.minor_category)
    if not category:
        raise HTTPException(
            status_code=404, 
            detail=f"Category '{parts.major_category}/{parts.minor_category}' not found"
        )
    
    # 새 Parts ID 생성 (제조사별 자동 증가)
    new_id = crud.get_next_parts_id(db, maker.id)
    
    # Parts 생성
    db_parts = crud.create_parts(
        db=db,
        parts_id=new_id,
        maker_id=maker.id,
        category_id=category.id,
        name=parts.name,
        unit=parts.unit,
        solo_price=parts.solo_price,
        ul=parts.ul,
        ce=parts.ce,
        kc=parts.kc,
        etc=parts.etc
    )
    
    # Response
    return {
        "item_code": f"{db_parts.maker_id}-{db_parts.id}",
        "id": db_parts.id,
        "maker_id": db_parts.maker_id,
        "maker_name": maker.name,
        "category_id": category.id,
        "major_category": category.major,
        "minor_category": category.minor,
        "name": db_parts.name,
        "unit": db_parts.unit,
        "solo_price": db_parts.solo_price,
        "ul": db_parts.certification.ul if db_parts.certification else False,
        "ce": db_parts.certification.ce if db_parts.certification else False,
        "kc": db_parts.certification.kc if db_parts.certification else False,
        "etc": db_parts.certification.etc if db_parts.certification else None,
        "created_at": db_parts.created_at
    }


@handler.get("/", response_model=schemas.PartsListResponse)
def get_parts_list(
    include_schema: bool = Query(False, description="schema 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    id: Optional[str] = Query(None, max_length=6),
    maker_id: Optional[str] = Query(None, max_length=4),
    name: Optional[str] = Query(None),
    unit: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None, ge=0),
    major: Optional[str] = Query(None),
    minor: Optional[str] = Query(None),
    ul: Optional[bool] = Query(None),
    ce: Optional[bool] = Query(None),
    kc: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Parts 목록 조회 (필터링 지원)
    
    - include_schema: true면 schema 포함
    - 11개 필터 파라미터 지원
    - updated_at DESC 정렬
    """
    # 필터 구성
    filters = {}
    if id: filters['id'] = id
    if maker_id: filters['maker_id'] = maker_id
    if name: filters['name'] = name
    if unit: filters['unit'] = unit
    if min_price: filters['min_price'] = min_price
    if max_price: filters['max_price'] = max_price
    if major: filters['major'] = major
    if minor: filters['minor'] = minor
    if ul is not None: filters['ul'] = ul
    if ce is not None: filters['ce'] = ce
    if kc is not None: filters['kc'] = kc
    
    # 조회
    total, parts_list = crud.get_parts_list(db, skip=skip, limit=limit, filters=filters)
    
    # Items 변환
    items = []
    for p in parts_list:
        items.append({
            "item_code": f"{p.maker_id}-{p.id}",
            "id": p.id,
            "maker_id": p.maker_id,
            "maker_name": p.maker.name,
            "category_id": p.category_id,
            "major_category": p.category.major,
            "minor_category": p.category.minor,
            "name": p.name,
            "unit": p.unit,
            "solo_price": p.solo_price,
            "ul": p.certification.ul if p.certification else False,
            "ce": p.certification.ce if p.certification else False,
            "kc": p.certification.kc if p.certification else False,
            "etc": p.certification.etc if p.certification else None
        })
    
    if include_schema:
        return {
            "schema": get_parts_schema(),
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


@handler.get("/{parts_id}/{maker_id}", response_model=schemas.PartsDetailResponse)
def get_parts(
    parts_id: str,
    maker_id: str,
    include_schema: bool = Query(False, description="schema 포함 여부"),
    db: Session = Depends(get_db)
):
    """
    Parts 단일 조회
    
    - parts_id + maker_id (복합 PK)
    - include_schema: true면 schema 포함
    """
    parts = crud.get_parts_by_id(db, parts_id, maker_id)
    if not parts:
        raise HTTPException(status_code=404, detail="Parts not found")
    
    # Response 데이터
    response_data = {
        "item_code": f"{parts.maker_id}-{parts.id}",
        "id": parts.id,
        "maker_id": parts.maker_id,
        "maker_name": parts.maker.name,
        "major_category": parts.category.major,
        "minor_category": parts.category.minor,
        "name": parts.name,
        "unit": parts.unit,
        "solo_price": parts.solo_price,
        "ul": parts.certification.ul if parts.certification else False,
        "ce": parts.certification.ce if parts.certification else False,
        "kc": parts.certification.kc if parts.certification else False,
        "etc": parts.certification.etc if parts.certification else None
    }
    
    if include_schema:
        return {
            "schema": get_parts_schema(),
            "item": response_data
        }
    
    return response_data


@handler.post("/search", response_model=schemas.PartsListResponse)
def search_parts(
    search: schemas.PartsSearch,
    db: Session = Depends(get_db)
):
    """
    Parts 검색 (여러 필드 OR 조건)
    
    - query: 검색어
    - search_fields: 검색 대상 필드 (name, id, maker_name, major, minor)
    - include_schema: true면 schema 포함
    """
    # 검색
    total, parts_list = crud.search_parts(
        db=db,
        query=search.query,
        search_fields=search.search_fields,
        skip=search.skip,
        limit=search.limit
    )
    
    # Items 변환
    items = []
    for p in parts_list:
        items.append({
            "item_code": f"{p.maker_id}-{p.id}",
            "id": p.id,
            "maker_id": p.maker_id,
            "maker_name": p.maker.name,
            "category_id": p.category_id,
            "major_category": p.category.major,
            "minor_category": p.category.minor,
            "name": p.name,
            "unit": p.unit,
            "solo_price": p.solo_price,
            "ul": p.certification.ul if p.certification else False,
            "ce": p.certification.ce if p.certification else False,
            "kc": p.certification.kc if p.certification else False,
            "etc": p.certification.etc if p.certification else None
        })
    
    if search.include_schema:
        return {
            "schema": get_parts_schema(),
            "total": total,
            "items": items,
            "skip": search.skip,
            "limit": search.limit
        }
    
    return {
        "total": total,
        "items": items,
        "skip": search.skip,
        "limit": search.limit
    }


@handler.put("/{parts_id}/{maker_id}", response_model=schemas.PartsUpdateResponse)
def update_parts(
    parts_id: str,
    maker_id: str,
    parts_update: schemas.PartsUpdate,
    db: Session = Depends(get_db)
):
    """
    Parts 수정 (부분 수정)
    
    - 모든 필드 선택적
    - category 변경 시 major + minor 둘 다 필요
    """
    # Parts 존재 확인
    existing_parts = crud.get_parts_by_id(db, parts_id, maker_id)
    if not existing_parts:
        raise HTTPException(status_code=404, detail="Parts not found")
    
    # Category 변경 확인
    category_id = None
    if parts_update.major_category and parts_update.minor_category:
        category = crud.get_category_by_major_minor(
            db, 
            parts_update.major_category, 
            parts_update.minor_category
        )
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"Category '{parts_update.major_category}/{parts_update.minor_category}' not found"
            )
        category_id = category.id
    
    # 수정
    updated_parts = crud.update_parts(
        db=db,
        parts_id=parts_id,
        maker_id=maker_id,
        category_id=category_id,
        name=parts_update.name,
        unit=parts_update.unit,
        solo_price=parts_update.solo_price,
        ul=parts_update.ul,
        ce=parts_update.ce,
        kc=parts_update.kc,
        etc=parts_update.etc
    )
    
    return {
        "item_code": f"{updated_parts.maker_id}-{updated_parts.id}",
        "id": updated_parts.id,
        "maker_id": updated_parts.maker_id,
        "maker_name": updated_parts.maker.name,
        "category_id": updated_parts.category_id,
        "major_category": updated_parts.category.major,
        "minor_category": updated_parts.category.minor,
        "name": updated_parts.name,
        "unit": updated_parts.unit,
        "solo_price": updated_parts.solo_price,
        "ul": updated_parts.certification.ul if updated_parts.certification else False,
        "ce": updated_parts.certification.ce if updated_parts.certification else False,
        "kc": updated_parts.certification.kc if updated_parts.certification else False,
        "etc": updated_parts.certification.etc if updated_parts.certification else None,
        "updated_at": updated_parts.updated_at
    }


@handler.delete("/{parts_id}/{maker_id}", response_model=schemas.PartsDeleteResponse)
def delete_parts(
    parts_id: str,
    maker_id: str,
    db: Session = Depends(get_db)
):
    """
    Parts 삭제 (CASCADE로 Certification도 삭제)
    """
    # Parts 존재 확인
    existing_parts = crud.get_parts_by_id(db, parts_id, maker_id)
    if not existing_parts:
        raise HTTPException(status_code=404, detail="Parts not found")
    
    item_code = f"{maker_id}-{parts_id}"
    
    # 삭제
    success = crud.delete_parts(db, parts_id, maker_id)
    if not success:
        raise HTTPException(status_code=404, detail="Parts not found")
    
    return {
        "message": "Parts deleted successfully",
        "deleted_item_code": item_code
    }