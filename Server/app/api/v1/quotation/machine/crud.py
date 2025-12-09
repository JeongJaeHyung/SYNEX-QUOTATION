# SYNEX+QUOTATION/Server/app/api/v1/quotation/machine/crud.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any
from uuid import UUID

from models.machine import Machine
from models.machine_resources import MachineResources
from models.resources import Resources
from models.maker import Maker
from models.category import Category
from models.certification import Certification


# ==================== CREATE ====================

def create_machine(
    db: Session,
    name: str,
    resources_data: List[Dict[str, Any]]
) -> Machine:
    """
    Machine과 MachineResources를 동시에 생성
    
    Args:
        db: Database session
        name: 기계명
        resources_data: 부품 목록 [{"maker_id": "J012", "resources_id": "000001", "solo_price": 22000, "quantity": 10}]
    
    Returns:
        생성된 Machine 객체
    """
    # 1. Machine 생성
    machine = Machine(name=name)
    db.add(machine)
    db.flush()  # ID 생성을 위해 flush
    
    # 2. quantity >= 1인 것만 필터링하여 MachineResources 생성
    for resource_data in resources_data:
        if resource_data.get("quantity", 0) >= 1:
            machine_resource = MachineResources(
                machine_id=machine.id,
                maker_id=resource_data["maker_id"],
                resources_id=resource_data["resources_id"],
                solo_price=resource_data["solo_price"],
                quantity=resource_data["quantity"]
            )
            db.add(machine_resource)
    
    db.commit()
    db.refresh(machine)
    
    return machine


# ==================== READ ====================

def get_machine_by_id(db: Session, machine_id: UUID) -> Optional[Machine]:
    """
    Machine ID로 상세 조회 (모든 관계 JOIN)
    
    Args:
        db: Database session
        machine_id: Machine UUID
    
    Returns:
        Machine 객체 또는 None
    """
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        return None
    
    # MachineResources와 관련 테이블들을 JOIN하여 조회
    machine_resources = db.query(MachineResources).options(
        joinedload(MachineResources.resource)
            .joinedload(Resources.maker),
        joinedload(MachineResources.resource)
            .joinedload(Resources.category),
        joinedload(MachineResources.resource)
            .joinedload(Resources.certification)
    ).filter(
        MachineResources.machine_id == machine_id
    ).all()
    
    # Machine 객체에 machine_resources 할당
    machine.machine_resources = machine_resources
    
    return machine


def get_machine_list(
    db: Session,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[Machine], int]:
    """
    Machine 목록 조회 (최근 업데이트 순)
    
    Args:
        db: Database session
        skip: 건너뛸 개수
        limit: 가져올 개수
    
    Returns:
        (Machine 리스트, 전체 개수)
    """
    # 전체 개수
    total = db.query(func.count(Machine.id)).scalar()
    
    # 목록 조회 (updated_at DESC)
    machines = db.query(Machine).order_by(
        Machine.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return machines, total


def search_machines(
    db: Session,
    search_query: str,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[Machine], int]:
    """
    Machine 이름으로 검색 (부분 매칭, 최근 업데이트 순)
    
    Args:
        db: Database session
        search_query: 검색어
        skip: 건너뛸 개수
        limit: 가져올 개수
    
    Returns:
        (Machine 리스트, 전체 개수)
    """
    # 검색 조건
    search_filter = Machine.name.ilike(f"%{search_query}%")
    
    # 전체 개수
    total = db.query(func.count(Machine.id)).filter(search_filter).scalar()
    
    # 목록 조회 (updated_at DESC)
    machines = db.query(Machine).filter(
        search_filter
    ).order_by(
        Machine.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return machines, total


# ==================== UPDATE ====================

def update_machine(
    db: Session,
    machine_id: UUID,
    name: Optional[str] = None,
    resources_data: Optional[List[Dict[str, Any]]] = None
) -> Optional[Machine]:
    """
    Machine 수정 (이름 및/또는 구성 부품)
    
    Args:
        db: Database session
        machine_id: Machine UUID
        name: 새 기계명 (Optional)
        resources_data: 새 부품 목록 (Optional)
    
    Returns:
        수정된 Machine 객체 또는 None
    """
    # Machine 조회
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        return None
    
    # 1. 이름 수정
    if name is not None:
        machine.name = name
    
    # 2. 부품 목록 수정 (전체 삭제 후 재생성)
    if resources_data is not None:
        # 기존 MachineResources 삭제
        db.query(MachineResources).filter(
            MachineResources.machine_id == machine_id
        ).delete()
        
        # quantity >= 1인 것만 필터링하여 새로 생성
        for resource_data in resources_data:
            if resource_data.get("quantity", 0) >= 1:
                machine_resource = MachineResources(
                    machine_id=machine_id,
                    maker_id=resource_data["maker_id"],
                    resources_id=resource_data["resources_id"],
                    solo_price=resource_data["solo_price"],
                    quantity=resource_data["quantity"]
                )
                db.add(machine_resource)
    
    db.commit()
    db.refresh(machine)
    
    return machine


# ==================== DELETE ====================

def delete_machine(db: Session, machine_id: UUID) -> bool:
    """
    Machine 삭제 (CASCADE로 MachineResources 자동 삭제)
    
    Args:
        db: Database session
        machine_id: Machine UUID
    
    Returns:
        삭제 성공 여부
    """
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    
    if not machine:
        return False
    
    db.delete(machine)
    db.commit()
    
    return True


# ==================== UTILITY ====================

def check_resources_exist(
    db: Session,
    maker_id: str,
    resources_id: str
) -> bool:
    """
    Resources 존재 여부 확인
    
    Args:
        db: Database session
        maker_id: 제조사 ID
        resources_id: 부품 ID
    
    Returns:
        존재 여부
    """
    return db.query(Resources).filter(
        Resources.maker_id == maker_id,
        Resources.id == resources_id
    ).first() is not None


def calculate_total_price(machine_resources: List[MachineResources]) -> int:
    """
    총 금액 계산
    
    Args:
        machine_resources: MachineResources 리스트
    
    Returns:
        총 금액 (sum of solo_price × quantity)
    """
    return sum(
        mr.solo_price * mr.quantity
        for mr in machine_resources
    )


def format_machine_resource_response(machine_resource: MachineResources) -> Dict[str, Any]:
    """
    MachineResource를 응답 형식으로 변환
    
    Args:
        machine_resource: MachineResources 객체
    
    Returns:
        응답 딕셔너리
    """
    resource = machine_resource.resource
    subtotal = machine_resource.solo_price * machine_resource.quantity
    
    return {
        "maker_id": machine_resource.maker_id,
        "resources_id": machine_resource.resources_id,
        "model_name": resource.name,
        "unit": resource.unit,
        "category_major": resource.category.major,
        "category_minor": resource.category.minor,
        "maker_name": resource.maker.name,
        "ul": resource.certification.ul if resource.certification else False,
        "ce": resource.certification.ce if resource.certification else False,
        "kc": resource.certification.kc if resource.certification else False,
        "etc": resource.certification.etc if resource.certification else None,
        "solo_price": machine_resource.solo_price,
        "quantity": machine_resource.quantity,
        "subtotal": subtotal
    }