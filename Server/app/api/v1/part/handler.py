# api/v1/parts/handler.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from database import get_db
from . import crud, schemas

handler = APIRouter()

def get_parts_schema() -> dict:
    """Parts 스키마 정의"""
    return {
        "item_code": {
            "title": "품목코드",
            "type": "string",
            "ratio": 2
        }, 
        "maker_name": {
            "title": "Maker",  # ✅ 제조사 → Maker
            "type": "string",
            "ratio": 2
        },
        "major_category": {
            "title": "Unit",  # ✅ 대분류 → Unit
            "type": "string",
            "ratio": 2
        },
        "minor_category": {
            "title": "품목",  # ✅ 중분류 → 품목
            "type": "string",
            "ratio": 2
        },
        "name": {
            "title": "모델명/규격",  # ✅ 부품명 → 모델명/규격
            "type": "string",
            "ratio": 3
        },
        "unit": {
            "title": "단위",
            "type": "string",
            "ratio": 1
        },
        "solo_price": {
            "title": "금액",  # ✅ 단가 → 금액
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
            "title": "기타",  # ✅ 기타인증 → 기타
            "type": "string",
            "ratio": 2
        }
    }


def convert_to_parts_response(resource) -> dict:
    """Resources 모델을 API 응답 형식으로 변환"""
    return {
        "item_code": f"{resource.maker_id}-{resource.id}",
        "id": resource.id,
        "maker_id": resource.maker_id,
        "maker_name": resource.maker.name,
        "major_category": resource.major,
        "minor_category": resource.minor,
        "name": resource.name,
        "unit": resource.unit,
        "solo_price": resource.solo_price,
        "ul": resource.certification.ul if resource.certification else False,
        "ce": resource.certification.ce if resource.certification else False,
        "kc": resource.certification.kc if resource.certification else False,
        "etc": resource.certification.etc if resource.certification else None,
        "created_at": resource.created_at,
        "updated_at": resource.updated_at
    }


@handler.post("", status_code=201)
def create_parts(
    parts_data: schemas.PartsCreate,
    db: Session = Depends(get_db)
):
    """새로운 Parts 등록"""
    
    # Maker 조회
    maker = crud.get_maker_by_name(db, parts_data.maker_name)
    if not maker:
        raise HTTPException(status_code=404, detail=f"Maker '{parts_data.maker_name}' not found")
    
    # Parts ID 생성
    parts_id = crud.get_next_parts_id(db, maker.id)
    
    # Parts 생성 (CRUD 호출)
    resource = crud.create_parts(
        db=db,
        parts_id=parts_id,
        maker_id=maker.id,
        major=parts_data.major_category,
        minor=parts_data.minor_category,
        name=parts_data.name,
        unit=parts_data.unit,
        solo_price=parts_data.solo_price,
        ul=parts_data.ul,
        ce=parts_data.ce,
        kc=parts_data.kc,
        etc=parts_data.certification_etc
    )
    
    return convert_to_parts_response(resource)


@handler.get("")
def get_parts_list(
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    id: Optional[str] = None,
    maker_id: Optional[str] = None,
    name: Optional[str] = None,
    unit: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    major: Optional[str] = None,
    minor: Optional[str] = None,
    ul: Optional[bool] = None,
    ce: Optional[bool] = None,
    kc: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Parts 목록 조회 (필터링 지원)"""
    
    # 필터 생성
    filters = schemas.PartsFilter(
        id=id,
        maker_id=maker_id,
        name=name,
        unit=unit,
        min_price=min_price,
        max_price=max_price,
        major=major,
        minor=minor,
        ul=ul,
        ce=ce,
        kc=kc
    )
    
    # 데이터 조회
    parts_list, total = crud.get_parts_list(db, filters, skip, limit)
    
    # 데이터 변환
    items = [convert_to_parts_response(part) for part in parts_list]
    
    # 응답 생성
    if include_schema:
        return {
            "schema": get_parts_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }
    else:
        return {
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }


@handler.get("/{parts_id}/{maker_id}")
def get_parts_detail(
    parts_id: str,
    maker_id: str,
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    db: Session = Depends(get_db)
):
    """특정 Parts 상세 조회"""
    
    parts = crud.get_parts_by_id(db, parts_id, maker_id)
    
    if not parts:
        raise HTTPException(status_code=404, detail="Parts not found")
    
    item = convert_to_parts_response(parts)
    
    if include_schema:
        return {
            "schema": get_parts_schema(),
            "item": item
        }
    else:
        return item


@handler.post("/search")
def search_parts(
    search_request: schemas.PartsSearchRequest,
    db: Session = Depends(get_db)
):
    """Parts 검색 (OR 조건)"""
    
    parts_list, total = crud.search_parts(
        db=db,
        query=search_request.query,
        search_fields=search_request.search_fields,
        skip=search_request.skip,
        limit=search_request.limit
    )
    
    # 데이터 변환
    items = [convert_to_parts_response(part) for part in parts_list]
    
    if search_request.include_schema:
        return {
            "schema": get_parts_schema(),
            "total": total,
            "items": items,
            "skip": search_request.skip,
            "limit": search_request.limit
        }
    else:
        return {
            "total": total,
            "items": items,
            "skip": search_request.skip,
            "limit": search_request.limit
        }


@handler.put("/{parts_id}/{maker_id}")
def update_parts(
    parts_id: str,
    maker_id: str,
    parts_update: schemas.PartsUpdate,
    db: Session = Depends(get_db)
):
    """Parts 정보 수정"""
    
    updated_parts = crud.update_parts(
        db=db,
        parts_id=parts_id,
        maker_id=maker_id,
        major=parts_update.major_category,
        minor=parts_update.minor_category,
        name=parts_update.name,
        unit=parts_update.unit,
        solo_price=parts_update.solo_price,
        ul=parts_update.ul,
        ce=parts_update.ce,
        kc=parts_update.kc,
        etc=parts_update.certification_etc
    )
    
    if not updated_parts:
        raise HTTPException(status_code=404, detail="Parts not found")
    
    return convert_to_parts_response(updated_parts)


@handler.delete("/{parts_id}/{maker_id}")
def delete_parts(
    parts_id: str,
    maker_id: str,
    db: Session = Depends(get_db)
):
    """Parts 삭제"""
    
    success = crud.delete_parts(db, parts_id, maker_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Parts not found")
    
    item_code = f"{maker_id}-{parts_id}"
    return {
        "message": "Parts deleted successfully",
        "deleted_item_code": item_code
    }