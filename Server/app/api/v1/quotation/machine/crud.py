# api/v1/quotation/machine/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from uuid import UUID
from typing import List, Optional
from models.machine import Machine
from models.machine_resources import MachineResources
from models.resources import Resources
from models.maker import Maker
from models.category import Category
from models.certification import Certification

# ============================================================
# Machine CRUD
# ============================================================

def create_machine(
    db: Session,
    name: str,
    creator: str,                    # ✅ 추가
    description: Optional[str],      # ✅ 추가
    resources: List[dict]
) -> Machine:
    """Machine 등록"""
    # Machine 생성
    machine = Machine(
        name=name,
        creator=creator,             # ✅ 추가
        description=description      # ✅ 추가
    )
    db.add(machine)
    db.flush()  # machine.id 생성
    
    # MachineResources 생성
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
    """Machine의 Resources 상세 정보 조회 (JOIN)"""
    results = (
        db.query(
            MachineResources.maker_id,
            MachineResources.resources_id,
            MachineResources.solo_price,
            MachineResources.quantity,
            Resources.name.label('model_name'),
            Resources.unit,
            Maker.name.label('maker_name'),
            Category.major.label('category_major'),
            Category.minor.label('category_minor'),
            Certification.ul,
            Certification.ce,
            Certification.kc,
            Certification.etc
        )
        .join(Resources, (MachineResources.maker_id == Resources.maker_id) & 
                         (MachineResources.resources_id == Resources.id))
        .join(Maker, Resources.maker_id == Maker.id)
        .join(Category, Resources.category_id == Category.id)
        .outerjoin(Certification, (Resources.id == Certification.resources_id) & 
                                   (Resources.maker_id == Certification.maker_id))
        .filter(MachineResources.machine_id == machine_id)
        .filter(MachineResources.quantity > 0)  # quantity 필터링
        .all()
    )
    
    # 결과 변환
    resources = []
    for r in results:
        resources.append({
            'item_code': f"{r.maker_id}-{r.resources_id}",
            'maker_id': r.maker_id,
            'resources_id': r.resources_id,
            'model_name': r.model_name,
            'unit': r.unit,
            'category_major': r.category_major,
            'category_minor': r.category_minor,
            'maker_name': r.maker_name,
            'ul': r.ul or False,
            'ce': r.ce or False,
            'kc': r.kc or False,
            'etc': r.etc,
            'solo_price': r.solo_price,
            'quantity': r.quantity,
            'subtotal': r.solo_price * r.quantity
        })
    
    return resources


def update_machine(
    db: Session,
    machine_id: UUID,
    name: Optional[str] = None,
    description: Optional[str] = None,      # ✅ 추가
    resources: Optional[List[dict]] = None
) -> Optional[Machine]:
    """Machine 수정"""
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        return None
    
    # Machine 정보 수정
    if name is not None:
        machine.name = name
    if description is not None:              # ✅ 추가
        machine.description = description
    
    # Resources 수정
    if resources is not None:
        # 기존 resources 삭제
        db.query(MachineResources).filter(
            MachineResources.machine_id == machine_id
        ).delete()
        
        # 새 resources 추가
        for resource in resources:
            machine_resource = MachineResources(
                machine_id=machine_id,
                maker_id=resource['maker_id'],
                resources_id=resource['resources_id'],
                solo_price=resource['solo_price'],
                quantity=resource['quantity']
            )
            db.add(machine_resource)
    
    db.commit()
    db.refresh(machine)
    return machine