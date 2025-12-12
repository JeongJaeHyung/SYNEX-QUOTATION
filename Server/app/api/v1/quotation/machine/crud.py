# api/v1/quotation/machine/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from uuid import UUID
from typing import List, Optional
from models.machine import Machine
from models.machine_resources import MachineResources
from models.resources import Resources
from models.maker import Maker
from models.certification import Certification

# ============================================================
# Machine CRUD
# ============================================================

def create_machine(
    db: Session,
    name: str,
    manufacturer: Optional[str],
    client: Optional[str],
    creator: str,
    description: Optional[str],
    resources: List[dict]
) -> Machine:
    """Machine 등록"""
    # 총액 계산
    total_price = sum(r['solo_price'] * r['quantity'] for r in resources)
    
    # Machine 생성
    machine = Machine(
        name=name,
        manufacturer=manufacturer,
        client=client,
        creator=creator,
        price=total_price,
        description=description
    )
    db.add(machine)
    db.flush()  # machine.id 생성
    
    # MachineResources 생성 (모든 타입 포함: 실제 부품 + SUMMARY + LABOR)
    for resource in resources:
        machine_resource = MachineResources(
            machine_id=machine.id,
            maker_id=resource['maker_id'],
            resources_id=resource['resources_id'],
            solo_price=resource['solo_price'],
            quantity=resource['quantity']
        )
        db.add(machine_resource)
    
    db.commit()
    db.refresh(machine)
    return machine


def get_machines(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> tuple[int, List[Machine]]:
    """Machine 목록 조회 (updated_at DESC)"""
    # Total count
    total = db.query(func.count(Machine.id)).scalar()
    
    # Query with pagination
    machines = (
        db.query(Machine)
        .order_by(desc(Machine.updated_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return total, machines


def search_machines(
    db: Session,
    search: str,
    skip: int = 0,
    limit: int = 100
) -> tuple[int, List[Machine]]:
    """Machine 검색 (name 부분 매칭)"""
    # Query
    query = db.query(Machine).filter(
        Machine.name.ilike(f"%{search}%")
    )
    
    # Total count
    total = query.count()
    
    # Results with pagination
    machines = (
        query
        .order_by(desc(Machine.updated_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return total, machines


def get_machine_by_id(db: Session, machine_id: UUID) -> Optional[Machine]:
    """Machine 상세 조회 (resources 포함)"""
    return (
        db.query(Machine)
        .options(joinedload(Machine.machine_resources))
        .filter(Machine.id == machine_id)
        .first()
    )


def get_machine_resources_detail(db: Session, machine_id: UUID) -> List[dict]:
    """
    Machine의 Resources 상세 정보 조회
    
    처리 방식:
    1. MachineResources에서 모든 항목 조회
    2. maker_id별 분기 처리:
       - 실제 부품: Resources 테이블 JOIN
       - SUMMARY: 가상 데이터 생성 (Local 자재, 운영 PC)
       - LABOR: 가상 데이터 생성 (인건비)
    """
    # MachineResources 모든 항목 조회
    machine_resources = (
        db.query(MachineResources)
        .filter(MachineResources.machine_id == machine_id)
        .filter(MachineResources.quantity > 0)
        .all()
    )
    
    resources = []
    
    for mr in machine_resources:
        if mr.maker_id == "SUMMARY":
            # ============ 집계 항목 (Local 자재, 운영 PC) ============
            item_name_map = {
                "LOCAL_MAT": "Local 자재",
                "OPERATION_PC": "운영 PC/주액 PC"
            }
            
            resources.append({
                'item_code': f"{mr.maker_id}-{mr.resources_id}",
                'maker_id': mr.maker_id,
                'resources_id': mr.resources_id,
                'model_name': item_name_map.get(mr.resources_id, mr.resources_id),
                'unit': 'ea',
                'category_major': '집계',
                'category_minor': '수동입력',
                'maker_name': '-',
                'ul': False,
                'ce': False,
                'kc': False,
                'etc': None,
                'solo_price': mr.solo_price,
                'quantity': mr.quantity,
                'subtotal': mr.solo_price * mr.quantity
            })
            
        elif mr.maker_id == "LABOR":
            # ============ 인건비 항목 ============
            # resources_id: LABOR_0, LABOR_1, ... 형식
            labor_name = mr.resources_id.replace("LABOR_", "인건비 ")
            
            resources.append({
                'item_code': f"{mr.maker_id}-{mr.resources_id}",
                'maker_id': mr.maker_id,
                'resources_id': mr.resources_id,
                'model_name': labor_name,
                'unit': 'M/D',
                'category_major': '인건비',
                'category_minor': '인건비',
                'maker_name': '-',
                'ul': False,
                'ce': False,
                'kc': False,
                'etc': None,
                'solo_price': mr.solo_price,
                'quantity': mr.quantity,
                'subtotal': mr.solo_price * mr.quantity
            })
            
        else:
            # ============ 실제 부품 - Resources 테이블 JOIN ============
            result = (
                db.query(
                    MachineResources.maker_id,
                    MachineResources.resources_id,
                    MachineResources.solo_price,
                    MachineResources.quantity,
                    Resources.name.label('model_name'),
                    Resources.unit,
                    Resources.major.label('category_major'),
                    Resources.minor.label('category_minor'),
                    Maker.name.label('maker_name'),
                    Certification.ul,
                    Certification.ce,
                    Certification.kc,
                    Certification.etc
                )
                .join(Resources, (MachineResources.maker_id == Resources.maker_id) & 
                                 (MachineResources.resources_id == Resources.id))
                .join(Maker, Resources.maker_id == Maker.id)
                .outerjoin(Certification, (Resources.id == Certification.resources_id) & 
                                           (Resources.maker_id == Certification.maker_id))
                .filter(MachineResources.machine_id == machine_id)
                .filter(MachineResources.maker_id == mr.maker_id)
                .filter(MachineResources.resources_id == mr.resources_id)
                .first()
            )
            
            if result:
                resources.append({
                    'item_code': f"{result.maker_id}-{result.resources_id}",
                    'maker_id': result.maker_id,
                    'resources_id': result.resources_id,
                    'model_name': result.model_name,
                    'unit': result.unit,
                    'category_major': result.category_major,
                    'category_minor': result.category_minor,
                    'maker_name': result.maker_name,
                    'ul': result.ul or False,
                    'ce': result.ce or False,
                    'kc': result.kc or False,
                    'etc': result.etc,
                    'solo_price': result.solo_price,
                    'quantity': result.quantity,
                    'subtotal': result.solo_price * result.quantity
                })
    
    return resources


def update_machine(
    db: Session,
    machine_id: UUID,
    name: Optional[str] = None,
    manufacturer: Optional[str] = None,
    client: Optional[str] = None,
    description: Optional[str] = None,
    resources: Optional[List[dict]] = None
) -> Optional[Machine]:
    """Machine 수정"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        return None
    
    # Machine 정보 수정
    if name is not None:
        machine.name = name
    if manufacturer is not None:
        machine.manufacturer = manufacturer
    if client is not None:
        machine.client = client
    if description is not None:
        machine.description = description
    
    # Resources 수정
    if resources is not None:
        # 기존 resources 삭제
        db.query(MachineResources).filter(
            MachineResources.machine_id == machine_id
        ).delete()
        
        # 새 resources 추가 (모든 타입 포함) 및 총액 재계산
        total_price = 0
        for resource in resources:
            machine_resource = MachineResources(
                machine_id=machine_id,
                maker_id=resource['maker_id'],
                resources_id=resource['resources_id'],
                solo_price=resource['solo_price'],
                quantity=resource['quantity']
            )
            db.add(machine_resource)
            total_price += resource['solo_price'] * resource['quantity']
        
        # 총액 업데이트
        machine.price = total_price
    
    db.commit()
    db.refresh(machine)
    return machine