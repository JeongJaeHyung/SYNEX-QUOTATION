# api/v1/quotation/detailed/crud.py
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.detailed import Detailed
from backend.models.detailed_resources import DetailedResources
from backend.models.price_compare_resources import PriceCompareResources

# ============================================================
# CRUD Functions
# ============================================================


def create_detailed(
    db: Session,
    folder_id: UUID,
    price_compare_id: UUID,
    title: str,
    creator: str,
    description: str | None,
) -> Detailed:
    """
    Detailed 생성 + DetailedResources 자동 생성

    1. Detailed 생성
    2. PriceCompareResources 조회
    3. DetailedResources 자동 생성
    """
    # 폴더당 최대 1개의 Detailed만 허용
    existing = db.query(Detailed).filter(Detailed.folder_id == folder_id).first()
    if existing:
        raise ValueError(
            "이 폴더에는 이미 을지가 존재합니다. 폴더당 최대 1개만 생성할 수 있습니다."
        )

    # 1. Detailed 생성
    detailed = Detailed(
        folder_id=folder_id,
        price_compare_id=price_compare_id,
        title=title,
        creator=creator,
        description=description,
    )
    db.add(detailed)
    db.flush()  # detailed.id 생성

    # 2. PriceCompareResources 조회
    price_compare_resources = (
        db.query(PriceCompareResources)
        .filter(PriceCompareResources.price_compare_id == price_compare_id)
        .all()
    )

    # 3. DetailedResources 자동 생성
    for resource in price_compare_resources:
        # solo_price 계산: upper가 0이면 1 곱하기
        solo_price = resource.quotation_solo_price * (
            resource.upper if resource.upper != 0 else 1
        )

        detailed_resource = DetailedResources(
            detailed_id=detailed.id,
            machine_name=resource.machine_name,
            major=resource.major,
            minor=resource.minor,
            unit=resource.quotation_unit,
            solo_price=int(solo_price),  # Float를 Int로 변환
            compare=resource.quotation_compare,
            description=resource.description or "",
        )
        db.add(detailed_resource)

    db.commit()
    db.refresh(detailed)
    return detailed


def get_detailed_by_id(db: Session, detailed_id: UUID) -> Detailed | None:
    """Detailed 단일 조회"""
    return db.query(Detailed).filter(Detailed.id == detailed_id).first()


def get_detailed_resources(db: Session, detailed_id: UUID) -> list[dict]:
    """
    DetailedResources 조회 (subtotal 포함)

    반환: machine_name, major, minor, unit, solo_price, compare, subtotal, description
    """
    resources = (
        db.query(DetailedResources)
        .filter(DetailedResources.detailed_id == detailed_id)
        .all()
    )

    result = []
    for r in resources:
        result.append(
            {
                "machine_name": r.machine_name,
                "major": r.major,
                "minor": r.minor,
                "unit": r.unit,
                "solo_price": r.solo_price,
                "compare": r.compare,
                "subtotal": r.solo_price * r.compare,  # 견적가 = 단가 * 수량
                "description": r.description,
            }
        )

    return result


def update_detailed(
    db: Session,
    detailed_id: UUID,
    title: str | None = None,
    creator: str | None = None,
    description: str | None = None,
    detailed_resources: list[dict] | None = None,
) -> Detailed | None:
    """
    Detailed 수정 (부분 수정)

    - title, creator, description 수정
    - detailed_resources 전체 교체 (선택)
    """
    detailed = get_detailed_by_id(db, detailed_id)
    if not detailed:
        return None

    # 기본 정보 수정
    if title is not None:
        detailed.title = title
    if creator is not None:
        detailed.creator = creator
    if description is not None:
        detailed.description = description

    # DetailedResources 수정 (제공된 경우)
    if detailed_resources is not None:
        # 기존 resources 삭제
        db.query(DetailedResources).filter(
            DetailedResources.detailed_id == detailed_id
        ).delete()

        # 새 resources 추가
        for resource in detailed_resources:
            detailed_resource = DetailedResources(
                detailed_id=detailed_id,
                machine_name=resource["machine_name"],
                major=resource["major"],
                minor=resource["minor"],
                unit=resource["unit"],
                solo_price=resource["solo_price"],
                compare=resource["compare"],
                description=resource.get("description", ""),
            )
            db.add(detailed_resource)

    db.commit()
    db.refresh(detailed)
    return detailed


def delete_detailed(db: Session, detailed_id: UUID) -> bool:
    """Detailed 삭제 (CASCADE로 DetailedResources도 자동 삭제)"""
    detailed = get_detailed_by_id(db, detailed_id)
    if not detailed:
        return False

    db.delete(detailed)
    db.commit()
    return True
