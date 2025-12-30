# api/v1/quotation/header/handler.py
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db

from . import crud, schemas

handler = APIRouter()

# ============================================================
# Schema 생성 함수
# ============================================================


def get_header_resources_schema() -> dict:
    """HeaderResources 스키마 정의"""
    return {
        "machine": {"title": "장비명", "type": "string", "ratio": 2},
        "name": {"title": "품명", "type": "string", "ratio": 2},
        "spac": {"title": "규격", "type": "string", "ratio": 2},
        "compare": {"title": "수량", "type": "integer", "ratio": 2},
        "unit": {"title": "단위", "type": "string", "ratio": 1},
        "solo_price": {"title": "단가", "type": "integer", "ratio": 1},
        "subtotal": {
            "title": "공급가액",
            "type": "integer",
            "format": "currency",
            "ratio": 2,
        },
        "description": {"title": "비고", "type": "string", "ratio": 2},
    }


# ============================================================
# Header Endpoints
# ============================================================


@handler.post("", status_code=201)
def create_header(header_data: schemas.HeaderCreate, db: Session = Depends(get_db)):
    """
    Header(갑지) 등록

    - folder_id: 폴더 ID (필수)
    - detailed_id: 을지 ID (필수)
    - title: 갑지 제목 (필수)
    - quotation_number: 견적번호 (선택)
    - creator: 작성자 (필수)
    - client: 고객사 (필수)
    - manufacturer: 장비사 (선택)
    - pic_name: 고객사 담당자명 (필수)
    - pic_position: 고객사 담당자 직급 (필수)

    자동 생성:
    1. DetailedResources 조회 → machine + major 그룹화
    2. 각 machine별로 자재비/인건비/경비 3개 항목 생성
    3. PriceCompareResources에서 관리비 조회 → 안전관리비 및 기업이윤
    4. price 자동 계산
    """
    try:
        # Header 생성
        quotation = crud.create_header(
            db=db,
            folder_id=header_data.folder_id,
            detailed_id=header_data.detailed_id,
            title=header_data.title,
            quotation_number=header_data.quotation_number,
            creator=header_data.creator,
            client=header_data.client,
            manufacturer=header_data.manufacturer,
            pic_name=header_data.pic_name,
            pic_position=header_data.pic_position,
        )

        # HeaderResources 조회
        resources = crud.get_header_resources(db, quotation.id)

        return {
            "id": quotation.id,
            "title": quotation.title,
            "quotation_number": quotation.quotation_number,
            "price": quotation.price,
            "best_nego_total": quotation.best_nego_total,
            "creator": quotation.creator,
            "client": quotation.client,
            "manufacturer": quotation.manufacturer,
            "pic_name": quotation.pic_name,
            "pic_position": quotation.pic_position,
            "description_1": quotation.description_1,
            "description_2": quotation.description_2,
            "updated_at": quotation.updated_at,
            "resource_count": len(resources),
            "header_resources": resources,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@handler.get("/{header_id}")
def get_header(
    header_id: UUID,
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    db: Session = Depends(get_db),
):
    """
    Header(갑지) 조회

    - header_id: Header ID (UUID)
    - include_schema: true면 resources 스키마 포함
    """
    quotation = crud.get_header_by_id(db, header_id)
    if not quotation:
        raise HTTPException(status_code=404, detail="Header not found")

    # HeaderResources 조회
    resources = crud.get_header_resources(db, header_id)

    if include_schema:
        return {
            "id": quotation.id,
            "title": quotation.title,
            "quotation_number": quotation.quotation_number,
            "price": quotation.price,
            "best_nego_total": quotation.best_nego_total,
            "creator": quotation.creator,
            "client": quotation.client,
            "manufacturer": quotation.manufacturer,
            "pic_name": quotation.pic_name,
            "pic_position": quotation.pic_position,
            "description_1": quotation.description_1,
            "description_2": quotation.description_2,
            "updated_at": quotation.updated_at,
            "resource_count": len(resources),
            "resources": {
                "schema": get_header_resources_schema(),
                "header_resources": resources,
            },
        }

    return {
        "id": quotation.id,
        "title": quotation.title,
        "quotation_number": quotation.quotation_number,
        "price": quotation.price,
        "best_nego_total": quotation.best_nego_total,
        "creator": quotation.creator,
        "client": quotation.client,
        "manufacturer": quotation.manufacturer,
        "pic_name": quotation.pic_name,
        "pic_position": quotation.pic_position,
        "description_1": quotation.description_1,
        "description_2": quotation.description_2,
        "updated_at": quotation.updated_at,
        "resource_count": len(resources),
        "header_resources": resources,
    }


@handler.put("/{header_id}")
def update_header(
    header_id: UUID, header_update: schemas.HeaderUpdate, db: Session = Depends(get_db)
):
    """
    Header(갑지) 수정

    - header_id: Header ID (UUID)
    - title: 갑지 제목 (선택)
    - creator: 작성자 (선택)
    - client: 고객사 (선택)
    - pic_name: 고객사 담당자명 (선택)
    - pic_position: 고객사 담당자 직급 (선택)
    - description_1: 설명1 (선택)
    - description_2: 설명2 (선택)
    - price: 갑지 총가격 (선택, header_resources 미제공 시 필수)
    - header_resources: HeaderResources 전체 교체 (선택)
    """
    # resources 데이터 변환
    resources_data = None
    if header_update.header_resources:
        resources_data = [r.dict() for r in header_update.header_resources]

    # 수정
    updated_quotation = crud.update_header(
        db=db,
        header_id=header_id,
        title=header_update.title,
        quotation_number=header_update.quotation_number,
        creator=header_update.creator,
        client=header_update.client,
        manufacturer=header_update.manufacturer,
        pic_name=header_update.pic_name,
        pic_position=header_update.pic_position,
        description_1=header_update.description_1,
        description_2=header_update.description_2,
        best_nego_total=header_update.best_nego_total,
        price=header_update.price,
        header_resources=resources_data,
    )

    if not updated_quotation:
        raise HTTPException(status_code=404, detail="Header not found")

    # HeaderResources 조회
    resources = crud.get_header_resources(db, header_id)

    return {
        "id": updated_quotation.id,
        "title": updated_quotation.title,
        "price": updated_quotation.price,
        "best_nego_total": updated_quotation.best_nego_total,
        "creator": updated_quotation.creator,
        "client": updated_quotation.client,
        "manufacturer": updated_quotation.manufacturer,
        "pic_name": updated_quotation.pic_name,
        "pic_position": updated_quotation.pic_position,
        "description_1": updated_quotation.description_1,
        "description_2": updated_quotation.description_2,
        "updated_at": updated_quotation.updated_at,
        "resource_count": len(resources),
        "header_resources": resources,
    }


@handler.delete("/{header_id}")
def delete_header(header_id: UUID, db: Session = Depends(get_db)):
    """
    Header(갑지) 삭제

    - header_id: Header ID (UUID)
    - CASCADE로 HeaderResources도 자동 삭제
    """
    success = crud.delete_header(db, header_id)
    if not success:
        raise HTTPException(status_code=404, detail="Header not found")

    return {"message": "Header deleted successfully", "deleted_id": str(header_id)}
