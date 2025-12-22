# api/v1/part/handler.py
#
# 부품(Resources) 관련 API 엔드포인트를 정의합니다.
# - 부품 생성, 목록 조회, 검색, 상세 조회, 수정, 삭제 API를 제공합니다.
# - DTO(Pydantic 스키마)와 CRUD(데이터베이스 작업) 계층을 연결하는 컨트롤러 역할을 합니다.
#

from fastapi import APIRouter, Depends, Query, HTTPException # FastAPI 라우터, 의존성 주입, 쿼리 파라미터, HTTP 예외 처리
from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위함
from typing import Optional, List # 타입 힌트 (선택적 인자, 리스트)
from backend.database import get_db # 데이터베이스 세션 의존성 주입
from . import crud, schemas # Part CRUD 함수 및 스키마(DTO) 임포트

# API 라우터 인스턴스 생성
handler = APIRouter()

# ============================================================
# 스키마 생성 헬퍼 함수
# ============================================================

def get_parts_schema() -> dict:
    """
    부품(Parts) 응답 DTO의 스키마 정의를 반환합니다.
    - 프론트엔드에서 테이블 헤더 및 컬럼 속성을 동적으로 생성할 때 사용될 수 있습니다.
    
    Returns:
        dict: 부품 스키마 정의 딕셔너리.
    """
    return {
        "item_code": {
            "title": "품목코드", # 테이블 헤더에 표시될 이름
            "type": "string",
            "ratio": 2 # 컬럼 너비 비율
        }, 
        "maker_name": {
            "title": "Maker",
            "type": "string",
            "ratio": 2
        },
        "major_category": {
            "title": "Unit",
            "type": "string",
            "ratio": 4
        },
        "minor_category": {
            "title": "품목",
            "type": "string",
            "ratio": 3
        },
        "name": {
            "title": "모델명/규격",
            "type": "string",
            "ratio": 10
        },
        "unit": {
            "title": "단위",
            "type": "string",
            "ratio": 0.1
        },
        "solo_price": {
            "title": "금액",
            "type": "integer",
            "format": "currency", # 통화 형식으로 포맷팅 지시자
            "ratio": 2
        },
        "ul": {
            "title": "UL",
            "type": "boolean",
            "ratio": 0.1
        },
        "ce": {
            "title": "CE",
            "type": "boolean",
            "ratio": 0.1
        },
        "kc": {
            "title": "KC",
            "type": "boolean",
            "ratio": 0.1
        },
        "etc": {
            "title": "기타",
            "type": "string",
            "ratio": 3
        }
    }

def convert_to_parts_response(resource) -> dict:
    """
    Resources ORM 모델 객체를 API 응답 형식의 딕셔너리(DTO)로 변환합니다.
    - 관계된 Maker, Certification 정보를 함께 포함합니다.
    
    Args:
        resource (Resources): 변환할 Resources ORM 모델 객체.
        
    Returns:
        dict: API 응답 형식에 맞는 부품 정보 딕셔너리.
    """
    return {
        "item_code": f"{resource.maker_id}-{resource.id}", # 복합 품목 코드
        "id": resource.id,
        "maker_id": resource.maker_id,
        "maker_name": resource.maker.name, # Maker 관계를 통해 제조사 이름 접근
        "major_category": resource.major,
        "minor_category": resource.minor,
        "name": resource.name,
        "unit": resource.unit,
        "solo_price": resource.solo_price,
        "display_order": getattr(resource, "display_order", None), # display_order 속성 가져오기
        # Certification 관계를 통해 인증 정보 접근 (없으면 기본값 False/None)
        "ul": resource.certification.ul if resource.certification else False,
        "ce": resource.certification.ce if resource.certification else False,
        "kc": resource.certification.kc if resource.certification else False,
        "etc": resource.certification.etc if resource.certification else None,
        "created_at": resource.created_at,
        "updated_at": resource.updated_at
    }


# ============================================================
# Parts Endpoints (부품 관련 API)
# ============================================================

@handler.post("/", status_code=201)
def create_parts(
    parts_data: schemas.PartsCreate, # 요청 바디는 PartsCreate 스키마를 따름
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    try:
        # --- Maker 조회 ---
        maker = crud.get_maker_by_name(db, parts_data.maker_name)
        if not maker:
            raise HTTPException(status_code=404, detail=f"제조사 '{parts_data.maker_name}'을(를) 찾을 수 없습니다.")
        
        # --- 중복 검사: major, minor, name ---
        existing = crud.get_parts_by_fields(db, parts_data.major_category, parts_data.minor_category, parts_data.name)
        if existing:
            item_code = f"{existing.maker_id}-{existing.id}"
            raise HTTPException(status_code=409, detail=f"중복된 부품이 존재합니다. item_code={item_code}")
        
        # --- Parts ID 생성 ---
        parts_id = crud.get_next_parts_id(db, maker.id)

        # --- Parts 생성 (CRUD 호출) ---
        resource = crud.create_parts(
            db=db,
            parts_id=parts_id,
            maker_id=maker.id, # 조회된 제조사의 실제 ID 사용
            major=parts_data.major_category,
            minor=parts_data.minor_category,
            name=parts_data.name,
            unit=parts_data.unit,
            solo_price=parts_data.solo_price,
            display_order=parts_data.display_order,
            ul=parts_data.ul,
            ce=parts_data.ce,
            kc=parts_data.kc,
            etc=parts_data.certification_etc
        )
        
        return convert_to_parts_response(resource) # 생성된 자원 객체를 응답 DTO로 변환하여 반환
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DEBUG: create_parts error: {str(e)}")


@handler.get("")
def get_parts_list(
    include_schema: bool = Query(False, description="응답에 스키마 정의를 포함할지 여부"),
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 최대 레코드 수"),
    id: Optional[str] = Query(None, description="부품 ID로 필터링"),
    maker_id: Optional[str] = Query(None, description="제조사 ID로 필터링"),
    name: Optional[str] = Query(None, description="모델명/규격으로 필터링"),
    unit: Optional[str] = Query(None, description="단위로 필터링"),
    min_price: Optional[int] = Query(None, ge=0, description="최소 단가"),
    max_price: Optional[int] = Query(None, ge=0, description="최대 단가"),
    major: Optional[str] = Query(None, description="대분류로 필터링"),
    minor: Optional[str] = Query(None, description="중분류로 필터링"),
    ul: Optional[bool] = Query(None, description="UL 인증 여부로 필터링"),
    ce: Optional[bool] = Query(None, description="CE 인증 여부로 필터링"),
    kc: Optional[bool] = Query(None, description="KC 인증 여부로 필터링"),
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    try:
        # 쿼리 파라미터를 기반으로 필터 객체를 생성합니다.
        filters = schemas.PartsFilter(
            id=id, maker_id=maker_id, name=name, unit=unit, min_price=min_price, max_price=max_price,
            major=major, minor=minor, ul=ul, ce=ce, kc=kc
        )
        
        parts_list, total = crud.get_parts_list(db, filters, skip=skip, limit=limit)
        
        # Resources 객체 리스트를 DTO 형식으로 변환합니다.
        items = [convert_to_parts_response(part) for part in parts_list]
        
        # 스키마 포함 옵션에 따라 응답을 구성합니다.
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DEBUG: get_parts_list error: {str(e)}")


@handler.get("/{parts_id}/{maker_id}")
def get_parts_detail(
    parts_id: str, # 경로 파라미터: 부품 ID
    maker_id: str, # 경로 파라미터: 제조사 ID
    include_schema: bool = Query(False, description="응답에 스키마 정의를 포함할지 여부"),
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    try:
        parts = crud.get_parts_by_id(db, parts_id, maker_id) # CRUD 함수를 통해 부품 조회
        
        if not parts:
            raise HTTPException(status_code=404, detail="부품을 찾을 수 없습니다.")
        
        item = convert_to_parts_response(parts) # Resources 객체를 응답 DTO로 변환
        
        # 스키마 포함 옵션에 따라 응답을 구성합니다.
        if include_schema:
            return {
                "schema": get_parts_schema(),
                "item": item
            }
        else:
            return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DEBUG: get_parts_detail error: {str(e)}")


@handler.post("/search")
def search_parts(
    search_request: schemas.PartsSearchRequest, # 요청 바디는 PartsSearchRequest 스키마를 따름
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    try:
        total, parts_list = crud.search_parts(
            db=db,
            query=search_request.query,
            search_fields=search_request.search_fields,
            skip=search_request.skip,
            limit=search_request.limit
        )
        
        # Resources 객체 리스트를 DTO 형식으로 변환합니다.
        items = [convert_to_parts_response(part) for part in parts_list]
        
        # 스키마 포함 옵션에 따라 응답을 구성합니다.
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DEBUG: search_parts error: {str(e)}")


@handler.put("/{parts_id}/{maker_id}")
def update_parts(
    parts_id: str, # 경로 파라미터: 부품 ID
    maker_id: str, # 경로 파라미터: 제조사 ID
    parts_update: schemas.PartsUpdate, # 요청 바디는 PartsUpdate 스키마를 따름
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    try:
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
            raise HTTPException(status_code=404, detail="부품을 찾을 수 없습니다.")
        
        return convert_to_parts_response(updated_parts) # 업데이트된 부품 객체를 응답 DTO로 변환하여 반환
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DEBUG: update_parts error: {str(e)}")


@handler.delete("/{parts_id}/{maker_id}")
def delete_parts(
    parts_id: str, # 경로 파라미터: 부품 ID
    maker_id: str, # 경로 파라미터: 제조사 ID
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    try:
        success = crud.delete_parts(db, parts_id, maker_id) # CRUD 함수를 통해 부품 삭제
        
        if not success:
            raise HTTPException(status_code=404, detail="부품을 찾을 수 없습니다.")
        
        item_code = f"{maker_id}-{parts_id}" # 삭제된 부품의 복합 품목 코드
        return {
            "message": "부품이 성공적으로 삭제되었습니다.",
            "deleted_item_code": item_code
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DEBUG: delete_parts error: {str(e)}")