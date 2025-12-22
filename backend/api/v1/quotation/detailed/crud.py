# api/v1/quotation/detailed/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional, List, Tuple
from backend.models.detailed import Detailed
from backend.models.detailed_resources import DetailedResources
from backend.models.price_compare_resources import PriceCompareResources

# ============================================================
# CRUD Functions
# ============================================================

def create_detailed(
    db: Session,
    general_id: UUID,
    price_compare_id: UUID,
    creator: str,
    description: Optional[str]
) -> Detailed:
    """
    Detailed 생성 + DetailedResources 자동 생성
    
    1. Detailed 생성
    2. PriceCompareResources 조회
    3. DetailedResources 자동 생성
    """
    # 1. Detailed 생성
    detailed = Detailed(
        general_id=general_id,
        price_compare_id=price_compare_id,
        creator=creator,
        description=description
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
        solo_price = resource.quotation_solo_price * (resource.upper if resource.upper != 0 else 1)
        
        detailed_resource = DetailedResources(
            detailed_id=detailed.id,
            machine_name=resource.machine_name,
            major=resource.major,
            minor=resource.minor,
            unit=resource.quotation_unit,
            solo_price=int(solo_price),  # Float를 Int로 변환
            compare=resource.quotation_compare,
            description=resource.description or ""
        )
        db.add(detailed_resource)
    
    db.commit()
    db.refresh(detailed)
    return detailed


def get_detailed_by_id(db: Session, detailed_id: UUID) -> Optional[Detailed]:
    """Detailed 단일 조회"""
    return db.query(Detailed).filter(Detailed.id == detailed_id).first()


def get_detailed_resources(db: Session, detailed_id: UUID) -> List[dict]:
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
        result.append({
            "machine_name": r.machine_name,
            "major": r.major,
            "minor": r.minor,
            "unit": r.unit,
            "solo_price": r.solo_price,
            "compare": r.compare,
            "subtotal": r.solo_price * r.compare,  # 견적가 = 단가 * 수량
            "description": r.description
        })
    
    return result


def update_detailed(
    db: Session,
    detailed_id: UUID,
    creator: Optional[str] = None,
    description: Optional[str] = None,
    detailed_resources: Optional[List[dict]] = None
) -> Optional[Detailed]:
    """
    Detailed 수정 (부분 수정)
    
    - creator, description 수정
    - detailed_resources 전체 교체 (선택)
    """
    detailed = get_detailed_by_id(db, detailed_id)
    if not detailed:
        return None
    
    # 기본 정보 수정
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
                machine_name=resource['machine_name'],
                major=resource['major'],
                minor=resource['minor'],
                unit=resource['unit'],
                solo_price=resource['solo_price'],
                compare=resource['compare'],
                description=resource.get('description', '')
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