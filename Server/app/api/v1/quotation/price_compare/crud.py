from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Dict, Tuple

# Models Import
from models.price_compare import PriceCompare
from models.price_compare_machine import PriceCompareMachine
from models.price_compare_resources import PriceCompareResources
from models.machine_resources import MachineResources
from models.machine import Machine # 💡 장비명 조회를 위해 필수

from . import schemas

# ============================================================
# Helper Logic: 초기 리소스 자동 계산 (BOM Aggregation)
# ============================================================
def calculate_initial_resources(db: Session, machine_ids: List[UUID]) -> List[dict]:
    """
    선택된 장비들의 BOM을 집계합니다.
    - Key: (machine_id, major, minor) -> 장비별/항목별 분리
    - description: 장비명(Machine.name) 자동 입력
    """
    
    # 1. 리소스 + 장비명 조인 조회
    results = (
        db.query(MachineResources, Machine.name)
        .join(Machine, MachineResources.machine_id == Machine.id)
        .filter(MachineResources.machine_id.in_(machine_ids))
        .all()
    )
    
    # 2. 메모리 상에서 집계
    # Key: (Machine_ID, Major, Minor) -> Value: {price, machine_name}
    aggregated: Dict[Tuple[UUID, str, str], Dict] = {}
    
    for res, machine_name in results:
        # 2-1. 대분류/중분류 결정
        is_labor = (res.maker_id == "LABOR") or (res.display_major and "인건비" in res.display_major)
        
        if is_labor:
            major = "인건비"
            minor = res.display_minor if res.display_minor else "인건비 합계"
        else:
            major = "자재비"
            minor = res.display_major if res.display_major else "기타 자재"
            
        # 2-2. 가격 계산
        total_price = res.solo_price * res.quantity
        
        # 2-3. 집계 (Key에 machine_id 포함 -> 장비별 분리!)
        key = (res.machine_id, major, minor)
        
        if key not in aggregated:
            aggregated[key] = {
                'price': 0,
                'machine_name': machine_name # 장비명 저장
            }
            
        aggregated[key]['price'] += total_price
            
    # 3. 결과 리스트 변환
    initial_data = []
    
    for (m_id, major, minor), data in aggregated.items():
        initial_data.append({
            "machine_id": m_id,  # 💡 DB에 저장될 machine_id
            "major": major,
            "minor": minor,
            "cost_solo_price": data['price'],
            "cost_unit": "식",
            "cost_compare": 1,
            "quotation_solo_price": data['price'],
            "quotation_unit": "식",
            "quotation_compare": 1,
            "upper": 0,
            
            # 💡 비고에 장비명 입력 (예: "주액기")
            "description": data['machine_name'] 
        })
        
    return initial_data

# ============================================================
# CRUD Functions
# ============================================================

def create_price_compare(db: Session, request: schemas.PriceCompareCreate) -> PriceCompare:
    """Price Compare 생성"""
    # 1. Header
    new_pc = PriceCompare(
        general_id=request.general_id,
        creator=request.creator,
        description=request.description
    )
    db.add(new_pc)
    db.flush() 
    
    # 2. Machine Links
    for m_id in request.machine_ids:
        db.add(PriceCompareMachine(price_compare_id=new_pc.id, machine_id=m_id))
        
    # 3. Resources (자동 계산)
    calculated_items = calculate_initial_resources(db, request.machine_ids)
    
    for item in calculated_items:
        resource = PriceCompareResources(
            price_compare_id=new_pc.id,
            
            # 💡 machine_id 저장
            machine_id=item['machine_id'],
            
            major=item['major'],
            minor=item['minor'],
            cost_solo_price=item['cost_solo_price'],
            cost_unit=item['cost_unit'],
            cost_compare=item['cost_compare'],
            quotation_solo_price=item['quotation_solo_price'],
            quotation_unit=item['quotation_unit'],
            quotation_compare=item['quotation_compare'],
            upper=item['upper'],
            description=item['description'] # 장비명
        )
        db.add(resource)
        
    db.commit()
    db.refresh(new_pc)
    return new_pc


def get_price_compare(db: Session, pc_id: UUID) -> PriceCompare:
    return db.query(PriceCompare).filter(PriceCompare.id == pc_id).first()


def update_price_compare_overwrite(
    db: Session, 
    pc_id: UUID, 
    request: schemas.PriceCompareUpdate
) -> PriceCompare:
    """수정 (Overwrite)"""
    pc = get_price_compare(db, pc_id)
    if not pc: return None
        
    # 1. Header Update
    pc.creator = request.creator
    pc.description = request.description
    
    # 2. Machine Links Re-insert
    db.query(PriceCompareMachine).filter(PriceCompareMachine.price_compare_id == pc_id).delete()
    for m_id in request.machine_ids:
        db.add(PriceCompareMachine(price_compare_id=pc_id, machine_id=m_id))
        
    # 3. Resources Re-insert
    db.query(PriceCompareResources).filter(PriceCompareResources.price_compare_id == pc_id).delete()
    
    target_data = []
    
    if request.price_compare_resources is not None:
        # Case A: 수동 덮어쓰기 (프론트에서 machine_id, description 다 받음)
        target_data = [res.model_dump() for res in request.price_compare_resources]
    else:
        # Case B: 자동 재계산 (장비명, machine_id 자동 생성)
        target_data = calculate_initial_resources(db, request.machine_ids)

    # 4. Save
    for item in target_data:
        new_res = PriceCompareResources(
            price_compare_id=pc_id,
            
            # 💡 machine_id 저장
            machine_id=item['machine_id'],
            
            major=item['major'],
            minor=item['minor'],
            cost_solo_price=item['cost_solo_price'],
            cost_unit=item['cost_unit'],
            cost_compare=item['cost_compare'],
            quotation_solo_price=item['quotation_solo_price'],
            quotation_unit=item['quotation_unit'],
            quotation_compare=item['quotation_compare'],
            upper=item['upper'],
            description=item.get('description')
        )
        db.add(new_res)
        
    db.commit()
    db.refresh(pc)
    return pc