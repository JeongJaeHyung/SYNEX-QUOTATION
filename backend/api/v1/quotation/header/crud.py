# api/v1/quotation/header/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional, List
from collections import defaultdict
from backend.models.header import Quotation
from backend.models.header_resources import QuotationResources
from backend.models.detailed import Detailed
from backend.models.detailed_resources import DetailedResources
from backend.models.price_compare_resources import PriceCompareResources

# ============================================================
# CRUD Functions
# ============================================================

def create_header(
    db: Session,
    general_id: UUID,
    detailed_id: UUID,
    title: str,
    creator: str,
    client: str,
    pic_name: str,
    pic_position: str
) -> Quotation:
    """
    Header(Quotation) 생성 + QuotationResources 자동 생성
    
    1. Detailed 조회 → price_compare_id 획득
    2. DetailedResources 조회 → machine_name + major로 그룹화
    3. 각 machine별로 자재비/인건비/경비 3개 항목 생성
    4. PriceCompareResources에서 관리비 조회 → 안전관리비 및 기업이윤 생성
    5. price 계산
    """
    # 1. Detailed 조회
    detailed = db.query(Detailed).filter(Detailed.id == detailed_id).first()
    if not detailed:
        raise ValueError("Detailed not found")
    
    price_compare_id = detailed.price_compare_id
    
    # 2. DetailedResources 조회
    detailed_resources = (
        db.query(DetailedResources)
        .filter(DetailedResources.detailed_id == detailed_id)
        .all()
    )
    
    # 3. machine_name + major로 그룹화 (subtotal 합산)
    groups = defaultdict(int)
    machines = set()
    
    for resource in detailed_resources:
        machines.add(resource.machine_name)
        key = (resource.machine_name, resource.major)
        groups[key] += resource.solo_price * resource.compare  # subtotal
    
    # 4. Quotation 생성
    quotation = Quotation(
        general_id=general_id,
        title=title,
        creator=creator,
        client=client,
        pic_name=pic_name,
        pic_position=pic_position,
        price=0  # 나중에 계산
    )
    db.add(quotation)
    db.flush()  # quotation.id 생성
    
    # 5. 각 machine별로 3개 항목 생성 (자재비, 인건비, 경비)
    quotation_resources_list = []
    
    for machine in sorted(machines):  # 정렬해서 일관성 유지
        # 자재비
        quotation_resources_list.append(QuotationResources(
            quotation_id=quotation.id,
            machine=machine,
            name="자재비",
            solo_price=groups.get((machine, "자재비"), 0),
            compare=1,
            unit="원",
            spac="",
            description=""
        ))
        
        # 인건비
        quotation_resources_list.append(QuotationResources(
            quotation_id=quotation.id,
            machine=machine,
            name="인건비",
            solo_price=groups.get((machine, "인건비"), 0),
            compare=1,
            unit="원",
            spac="",
            description=""
        ))
        
        # 경비 (출장 경비 → 경비)
        quotation_resources_list.append(QuotationResources(
            quotation_id=quotation.id,
            machine=machine,
            name="경비",
            solo_price=groups.get((machine, "출장 경비"), 0),
            compare=1,
            unit="원",
            spac="",
            description=""
        ))
    
    # 6. PriceCompareResources에서 관리비 조회
    admin_cost = (
        db.query(PriceCompareResources)
        .filter(
            PriceCompareResources.price_compare_id == price_compare_id,
            PriceCompareResources.major == "출장경비"
        )
        .first()
    )
    
    # 안전관리비 및 기업이윤 추가
    quotation_resources_list.append(QuotationResources(
        quotation_id=quotation.id,
        machine="",
        name="안전관리비 및 기업이윤",
        solo_price=int(admin_cost.quotation_solo_price) if admin_cost else 0,
        compare=1,
        unit="원",
        spac="",
        description=""
    ))
    
    # 7. QuotationResources 저장
    for qr in quotation_resources_list:
        db.add(qr)
    
    # 8. price 계산
    total_price = sum(qr.solo_price * qr.compare for qr in quotation_resources_list)
    quotation.price = total_price
    
    db.commit()
    db.refresh(quotation)
    return quotation


def get_header_by_id(db: Session, header_id: UUID) -> Optional[Quotation]:
    """Header(Quotation) 단일 조회"""
    return db.query(Quotation).filter(Quotation.id == header_id).first()


def get_header_resources(db: Session, header_id: UUID) -> List[dict]:
    """
    QuotationResources 조회 (subtotal 포함)
    
    반환: machine, name, spac, compare, unit, solo_price, subtotal, description
    """
    resources = (
        db.query(QuotationResources)
        .filter(QuotationResources.quotation_id == header_id)
        .all()
    )
    
    result = []
    for r in resources:
        result.append({
            "machine": r.machine,
            "name": r.name,
            "spac": r.spac,
            "compare": r.compare,
            "unit": r.unit,
            "solo_price": r.solo_price,
            "subtotal": r.solo_price * r.compare,
            "description": r.description
        })
    
    return result


def update_header(
    db: Session,
    header_id: UUID,
    title: Optional[str] = None,
    creator: Optional[str] = None,
    client: Optional[str] = None,
    pic_name: Optional[str] = None,
    pic_position: Optional[str] = None,
    description_1: Optional[str] = None,
    description_2: Optional[str] = None,
    quotation_resources: Optional[List[dict]] = None
) -> Optional[Quotation]:
    """
    Header(Quotation) 수정 (부분 수정)
    
    - 기본 정보 수정
    - quotation_resources 전체 교체 (선택)
    - price 자동 재계산
    """
    quotation = get_header_by_id(db, header_id)
    if not quotation:
        return None
    
    # 기본 정보 수정
    if title is not None:
        quotation.title = title
    if creator is not None:
        quotation.creator = creator
    if client is not None:
        quotation.client = client
    if pic_name is not None:
        quotation.pic_name = pic_name
    if pic_position is not None:
        quotation.pic_position = pic_position
    if description_1 is not None:
        quotation.description_1 = description_1
    if description_2 is not None:
        quotation.description_2 = description_2
    
    # QuotationResources 수정 (제공된 경우)
    if quotation_resources is not None:
        # 기존 resources 삭제
        db.query(QuotationResources).filter(
            QuotationResources.quotation_id == header_id
        ).delete()
        
        # 새 resources 추가
        for resource in quotation_resources:
            qr = QuotationResources(
                quotation_id=header_id,
                machine=resource['machine'],
                name=resource['name'],
                spac=resource.get('spac', ''),
                compare=resource['compare'],
                unit=resource['unit'],
                solo_price=resource['solo_price'],
                description=resource.get('description', '')
            )
            db.add(qr)
        
        # price 재계산
        total_price = sum(r['solo_price'] * r['compare'] for r in quotation_resources)
        quotation.price = total_price
    
    db.commit()
    db.refresh(quotation)
    return quotation


def delete_header(db: Session, header_id: UUID) -> bool:
    """Header(Quotation) 삭제 (CASCADE로 QuotationResources도 자동 삭제)"""
    quotation = get_header_by_id(db, header_id)
    if not quotation:
        return False
    
    db.delete(quotation)
    db.commit()
    return True