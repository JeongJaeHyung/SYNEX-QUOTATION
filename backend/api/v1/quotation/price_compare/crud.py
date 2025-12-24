# SYNEX+QUOTATION/backend/api/v1/quotation/price_compare/crud.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Tuple

# Models Import
from backend.models.price_compare import PriceCompare
from backend.models.price_compare_machine import PriceCompareMachine
from backend.models.price_compare_resources import PriceCompareResources
from backend.models.machine_resources import MachineResources
from backend.models.machine import Machine
from . import schemas

# ============================================================
# Helper Logic: 초기 리소스 자동 계산 (BOM Aggregation)
# ============================================================
def calculate_initial_resources(db: Session, machine_ids: List[UUID]) -> List[dict]:
    """
    선택된 장비들의 BOM을 집계하고 출장경비 및 관리비를 추가합니다.
    - 인건비: major는 유지하고, minor(구분)는 model_name을 가져옵니다.
    - 자재비: major는 "자재비"로 고정하고, minor(구분)는 원본 대분류를 가져와 집계합니다.
    - 견적 단가(quotation_solo_price): 내정가 합계에서 15% 증가된 금액으로 초기화합니다. 💡
    """
    
    # 1. 리소스 + 장비명 조회
    results = (
        db.query(MachineResources, Machine.name)
        .join(Machine, MachineResources.machine_id == Machine.id)
        .filter(MachineResources.machine_id.in_(machine_ids))
        .all()
    )
    
    # 2. 메모리 상에서 집계
    aggregated: Dict[Tuple, Dict] = {}
    
    for res, machine_name in results:
        is_labor = (res.maker_id == "LABOR") or (res.display_major and "인건비" in res.display_major)
        
        if is_labor:
            major = res.display_major if res.display_major else "인건비"
            minor = res.display_model_name if res.display_model_name else "인건비 상세"
        else:
            major = "자재비"
            minor = res.display_major if res.display_major else "기타 자재"
            
        key = (res.machine_id, machine_name, major, minor)
        
        if key not in aggregated:
            aggregated[key] = {
                'price': 0,
                'display_unit': res.display_unit if res.display_unit else ("M/D" if is_labor else "ea")
            }
        
        # 합계 금액 계산 (내정가 기준)
        aggregated[key]['price'] += (res.solo_price * res.quantity)
            
    # 3. 결과 리스트 변환 (15% 할증 로직 적용) 💡
    initial_data = []
    for (m_id, m_name, major, minor), data in aggregated.items():
        base_price = data['price']
        # 💡 요구사항 반영: 견적 단가를 내정가보다 15% 증가된 금액으로 저장
        increased_price = int(base_price * 1.15)
        
        initial_data.append({
            "machine_id": m_id,
            "machine_name": m_name,
            "major": major,
            "minor": minor,
            "cost_solo_price": base_price,
            "cost_unit": data['display_unit'],
            "cost_compare": 1,
            "quotation_solo_price": increased_price, # 💡 15% 증가 반영
            "quotation_unit": data['display_unit'],
            "quotation_compare": 1,
            "upper": 15.0,
            "description": None
        })
    
    # 4. 가상 항목 추가 (출장경비 & 관리비)
    first_machine_id = machine_ids[0] if machine_ids else None
    
    # 4-1. 출장경비 리스트
    business_trip_items = ["교통비", "식대", "운송비", "숙박비"]
    for item in business_trip_items:
        initial_data.append({
            "machine_id": first_machine_id,
            "machine_name": item,
            "major": "출장경비",
            "minor": item,
            "cost_solo_price": 0,
            "cost_unit": "원",
            "cost_compare": 1,
            "quotation_solo_price": 0,
            "quotation_unit": "원",
            "quotation_compare": 1,
            "upper": 15.0,
            "description": ""
        })

    # 4-2. 관리비 리스트
    overhead_items = ["일반관리비", "기업이윤"]
    for item in overhead_items:
        initial_data.append({
            "machine_id": first_machine_id,
            "machine_name": item,
            "major": "관리비",
            "minor": item,
            "cost_solo_price": 0,
            "cost_unit": "원",
            "cost_compare": 1,
            "quotation_solo_price": 0,
            "quotation_unit": "원",
            "quotation_compare": 1,
            "upper": 15.0,
            "description": ""
        })
        
    return initial_data

# ============================================================
# CRUD Functions
# ============================================================

def create_price_compare(db: Session, request: schemas.PriceCompareCreate) -> PriceCompare:
    new_pc = PriceCompare(
        general_id=request.general_id,
        creator=request.creator,
        description=request.description
    )
    db.add(new_pc)
    db.flush() 
    
    for m_id in request.machine_ids:
        db.add(PriceCompareMachine(price_compare_id=new_pc.id, machine_id=m_id))
        
    calculated_items = calculate_initial_resources(db, request.machine_ids)
    for item in calculated_items:
        db.add(PriceCompareResources(price_compare_id=new_pc.id, **item))
        
    db.commit()
    db.refresh(new_pc)
    return new_pc

def get_price_compare(db: Session, pc_id: UUID) -> PriceCompare:
    return db.query(PriceCompare).filter(PriceCompare.id == pc_id).first()

def update_price_compare_overwrite(db: Session, pc_id: UUID, request: schemas.PriceCompareUpdate) -> PriceCompare:
    pc = get_price_compare(db, pc_id)
    if not pc: return None
        
    pc.creator = request.creator
    pc.description = request.description
    
    db.query(PriceCompareMachine).filter(PriceCompareMachine.price_compare_id == pc_id).delete()
    for m_id in request.machine_ids:
        db.add(PriceCompareMachine(price_compare_id=pc_id, machine_id=m_id))
        
    db.query(PriceCompareResources).filter(PriceCompareResources.price_compare_id == pc_id).delete()
    
    if request.price_compare_resources is not None:
        target_data = [res.model_dump() for res in request.price_compare_resources]
    else:
        target_data = calculate_initial_resources(db, request.machine_ids)

    for item in target_data:
        db.add(PriceCompareResources(price_compare_id=pc_id, **item))
        
    db.commit()
    db.refresh(pc)
    return pc