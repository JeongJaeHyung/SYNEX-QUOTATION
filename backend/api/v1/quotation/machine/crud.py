# api/v1/quotation/machine/crud.py
#
# 견적서(Machine) 및 견적서 구성 자재(MachineResources) 데이터베이스 작업을 위한 CRUD 함수를 정의합니다.
# - 견적서 생성, 조회, 검색, 수정 기능을 제공합니다.
# - 특히 견적서에 포함된 자재 상세 정보를 처리하는 로직을 포함합니다.
#

from sqlalchemy.orm import Session, joinedload # 데이터베이스 세션 및 관계된 객체 미리 로드
from sqlalchemy import func, desc # SQLAlchemy 함수 (예: count, 내림차순 정렬) 임포트
from uuid import UUID # UUID 타입 사용 (견적서 ID)
from typing import List, Optional, Tuple # 타입 힌트
from backend.models.machine import Machine # Machine 모델 임포트
from backend.models.machine_resources import MachineResources # MachineResources 모델 임포트
from backend.models.resources import Resources # Resources 모델 임포트 (자재 마스터)
from backend.models.maker import Maker # Maker 모델 임포트 (제조사)
from backend.models.certification import Certification # Certification 모델 임포트 (인증 정보)

# ============================================================
# Machine CRUD 함수
# ============================================================

def create_machine(
    db: Session,
    name: str, # 장비/견적서 이름
    manufacturer: Optional[str], # 장비사
    client: Optional[str], # 고객사
    creator: str, # 작성자
    description: Optional[str], # 비고
    resources: List[dict] # 견적서에 포함될 자재 목록 (MachineResources 데이터)
) -> Machine:
    """
    새로운 견적서(Machine)를 생성하고, 해당 견적서에 포함되는 자재(MachineResources)들을 함께 저장합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        (위에 정의된 인자들)
        
    Returns:
        Machine: 생성된 Machine 객체.
    """
    # 견적서에 포함된 모든 자재의 단가와 수량을 바탕으로 총액을 계산합니다.
    total_price = sum(r['solo_price'] * r['quantity'] for r in resources)
    
    # Machine 모델 인스턴스를 생성합니다.
    machine = Machine(
        name=name,
        manufacturer=manufacturer,
        client=client,
        creator=creator,
        price=total_price, # 계산된 총액 저장
        description=description
    )
    db.add(machine) # 세션에 Machine 객체 추가
    db.flush()  # machine.id를 즉시 할당받기 위해 플러시합니다. (MachineResources 생성에 필요)
    
    # 전달받은 자재 목록(resources)을 바탕으로 MachineResources들을 생성합니다.
    # 인건비, SUMMARY 항목 (Local 자재, 운영 PC), 일반 부품 등 모든 타입의 자재가 포함됩니다.
    for index, resource in enumerate(resources):
        machine_resource = MachineResources(
            machine_id=machine.id, # 위에서 생성된 Machine의 ID
            maker_id=resource['maker_id'],
            resources_id=resource['resources_id'],
            solo_price=resource['solo_price'],
            quantity=resource['quantity'],
            order_index=index, # 목록 내 표시 순서
            # 견적서 화면 표시용 스냅샷 데이터
            display_major=resource.get("display_major"),
            display_minor=resource.get("display_minor"),
            display_model_name=resource.get("display_model_name"),
            display_maker_name=resource.get("display_maker_name"),
            display_unit=resource.get("display_unit"),
        )
        db.add(machine_resource) # 세션에 MachineResources 객체 추가
    
    db.commit() # 트랜잭션 커밋 (DB에 모든 변경사항 반영)
    db.refresh(machine) # Machine 객체를 최신 상태로 새로고침
    return machine


def get_machines(
    db: Session,
    skip: int = 0, # 조회 시작 지점 (OFFSET)
    limit: int = 100 # 조회할 최대 개수 (LIMIT)
) -> Tuple[int, List[Machine]]:
    """
    데이터베이스에서 모든 견적서(Machine) 목록을 조회합니다.
    페이징 기능을 지원하며, 총 견적서 개수와 목록을 반환합니다.
    최신 수정일 기준으로 내림차순 정렬됩니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        
    Returns:
        Tuple[int, List[Machine]]: (총 견적서 개수, Machine 객체 리스트).
    """
    total = db.query(func.count(Machine.id)).scalar() # 총 견적서 개수 조회
    
    # 수정일(updated_at) 기준 내림차순으로 정렬하여 견적서 목록을 페이징하여 조회합니다.
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
    search: str, # 검색어
    skip: int = 0,
    limit: int = 100
) -> Tuple[int, List[Machine]]:
    """
    견적서(Machine) 이름을 사용하여 견적서 목록을 검색합니다.
    부분 매칭 및 페이징 기능을 지원합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        search (str): 견적서 이름에서 검색할 문자열.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        
    Returns:
        Tuple[int, List[Machine]]: (총 검색 결과 개수, 검색된 Machine 객체 리스트).
    """
    query = db.query(Machine).filter(
        Machine.name.ilike(f"%{search}%") # 견적서 이름 부분 매칭 (대소문자 구분 없음)
    )
    
    total = query.count() # 검색 결과의 총 개수
    
    # 수정일(updated_at) 기준 내림차순으로 정렬하여 검색된 견적서 목록을 페이징하여 조회합니다.
    machines = (
        query
        .order_by(desc(Machine.updated_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return total, machines


def get_machine_by_id(db: Session, machine_id: UUID) -> Optional[Machine]:
    """
    견적서 ID를 사용하여 데이터베이스에서 단일 견적서(Machine) 상세 정보를 조회합니다.
    - `joinedload(Machine.machine_resources)`를 사용하여 MachineResources를 한 번의 쿼리로 함께 로드합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        machine_id (UUID): 조회할 견적서 ID.
        
    Returns:
        Optional[Machine]: 조회된 Machine 객체, 없으면 None.
    """
    return (
        db.query(Machine)
        .options(joinedload(Machine.machine_resources)) # MachineResources 관계를 Eager Loading
        .filter(Machine.id == machine_id) # 견적서 ID로 필터링
        .first() # 첫 번째 결과 반환
    )


def get_machine_resources_detail(db: Session, machine_id: UUID) -> List[dict]:
    """
    특정 견적서(Machine)에 포함된 자재(Resources)의 상세 정보를 조회합니다.
    - MachineResources 테이블의 정보를 기반으로, 실제 Resources 및 Maker, Certification 정보를 조인하여 반환합니다.
    - SUMMARY(집계) 및 LABOR(인건비) 항목은 가상 데이터를 생성하여 반환합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        machine_id (UUID): 조회할 견적서 ID.
        
    Returns:
        List[dict]: 견적서에 포함된 자재들의 상세 정보 딕셔너리 리스트.
    """
    # 주어진 machine_id에 해당하는 모든 MachineResources를 order_index 순으로 조회합니다.
    machine_resources = (
        db.query(MachineResources)
        .filter(MachineResources.machine_id == machine_id)
        .filter(MachineResources.quantity > 0) # 수량이 0보다 큰 항목만 포함
        .order_by(MachineResources.order_index.asc()) # 표시 순서대로 정렬
        .all()
    )
    
    resources = [] # 최종 반환될 자재 상세 정보 리스트
    
    for mr in machine_resources:
        # --- SUMMARY 타입 (Local 자재, 운영 PC 등) 처리 ---
        # 이 항목들은 실제 Resources 테이블에 매핑되지 않고, 가상으로 생성됩니다.
        if mr.maker_id == "SUMMARY" or mr.maker_id == "T000": # T000도 SUMMARY처럼 처리될 수 있음 (관례)
            item_name_map = {
                "LOCAL_MAT": "Local 자재",
                "OPERATION_PC": "운영 PC/주액 PC",
                # "CABLE_ETC"도 여기에 추가될 수 있음
            }
            
            resources.append({
                'item_code': f"{mr.maker_id}-{mr.resources_id}",
                'maker_id': mr.maker_id,
                'resources_id': mr.resources_id,
                'model_name': mr.display_model_name or item_name_map.get(mr.resources_id, mr.resources_id), # 화면 표시용 이름
                'unit': mr.display_unit or 'ea',
                'category_major': mr.display_major or '집계',
                'category_minor': mr.display_minor or '수동입력',
                'maker_name': mr.display_maker_name or '-',
                'ul': False,
                'ce': False,
                'kc': False,
                'etc': None, # SUMMARY 항목은 기타 인증/비고 없음
                'solo_price': mr.solo_price,
                'quantity': mr.quantity,
                'subtotal': mr.solo_price * mr.quantity
            })
            
        # --- LABOR 타입 (인건비) 처리 ---
        # 인건비 항목 역시 가상으로 데이터를 생성합니다.
        elif mr.maker_id == "LABOR" or mr.maker_id == "T000": # T000이 LABOR로도 쓰일 수 있음
            # resources_id가 "LABOR_0", "LABOR_1"과 같은 형식일 경우 "인건비 " 접두사를 붙여 이름 생성
            labor_name = mr.display_model_name or mr.resources_id.replace("LABOR_", "인건비 ")
            
            resources.append({
                'item_code': f"{mr.maker_id}-{mr.resources_id}",
                'maker_id': mr.maker_id,
                'resources_id': mr.resources_id,
                'model_name': labor_name,
                'unit': mr.display_unit or 'M/D',
                'category_major': mr.display_major or '인건비',
                'category_minor': mr.display_minor or '인건비',
                'maker_name': mr.display_maker_name or '-',
                'ul': False,
                'ce': False,
                'kc': False,
                'etc': None, # 인건비는 기타 인증/비고 없음
                'solo_price': mr.solo_price,
                'quantity': mr.quantity,
                'subtotal': mr.solo_price * mr.quantity
            })
            
        # --- 일반 부품 처리 ---
        # 실제 Resources 테이블과 Maker, Certification 테이블을 조인하여 상세 정보를 가져옵니다.
        else:
            result = (
                db.query(
                    MachineResources.maker_id,
                    MachineResources.resources_id,
                    MachineResources.solo_price,
                    MachineResources.quantity,
                    MachineResources.display_major,
                    MachineResources.display_minor,
                    MachineResources.display_model_name,
                    MachineResources.display_maker_name,
                    MachineResources.display_unit,
                    Resources.name.label('model_name'), # Resources 마스터의 이름
                    Resources.unit, # Resources 마스터의 단위
                    Resources.major.label('category_major'), # Resources 마스터의 대분류
                    Resources.minor.label('category_minor'), # Resources 마스터의 중분류
                    Maker.name.label('maker_name'), # Maker의 이름
                    Certification.ul, # 인증 정보
                    Certification.ce,
                    Certification.kc,
                    Certification.etc
                )
                .join(Resources, (MachineResources.maker_id == Resources.maker_id) & # Resources와 조인
                                 (MachineResources.resources_id == Resources.id))
                .join(Maker, Resources.maker_id == Maker.id) # Maker와 조인
                .outerjoin(Certification, (Resources.id == Certification.resources_id) & # Certification과 Outer Join (인증 정보가 없을 수도 있음)
                                           (Resources.maker_id == Certification.maker_id))
                .filter(MachineResources.machine_id == machine_id) # 해당 견적서의 자재만 필터링
                .filter(MachineResources.maker_id == mr.maker_id) # 현재 처리 중인 MachineResources와 일치하는 자재
                .filter(MachineResources.resources_id == mr.resources_id)
                .first() # 단일 결과 반환
            )
            
            if result:
                # MachineResources에 저장된 display_* 필드를 우선 사용하고, 없으면 Resources 마스터의 정보를 사용합니다.
                model_name = mr.display_model_name or result.model_name
                unit = mr.display_unit or result.unit
                category_major = mr.display_major or result.category_major
                category_minor = mr.display_minor or result.category_minor
                maker_name = mr.display_maker_name or result.maker_name
                
                resources.append({
                    'item_code': f"{result.maker_id}-{result.resources_id}",
                    'maker_id': result.maker_id,
                    'resources_id': result.resources_id,
                    'model_name': model_name,
                    'unit': unit,
                    'category_major': category_major,
                    'category_minor': category_minor,
                    'maker_name': maker_name,
                    'ul': result.ul or False,
                    'ce': result.ce or False,
                    'kc': result.kc or False,
                    'etc': result.etc,
                    'solo_price': result.solo_price,
                    'quantity': result.quantity,
                    'subtotal': result.solo_price * result.quantity # 소계 계산
                })
    
    return resources


def update_machine(
    db: Session,
    machine_id: UUID, # 업데이트할 견적서 ID
    name: Optional[str] = None,
    manufacturer: Optional[str] = None,
    client: Optional[str] = None,
    description: Optional[str] = None,
    resources: Optional[List[dict]] = None # 업데이트할 자재 목록
) -> Optional[Machine]:
    """
    기존 견적서(Machine) 정보를 업데이트합니다.
    - 견적서의 기본 정보(이름, 장비사 등)를 수정합니다.
    - 견적서 구성 자재(MachineResources)를 완전히 대체합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        machine_id (UUID): 업데이트할 견적서 ID.
        (위에 정의된 인자들)
        
    Returns:
        Optional[Machine]: 업데이트된 Machine 객체, 없으면 None.
    """
    machine = db.query(Machine).filter(Machine.id == machine_id).first() # 견적서 조회
    if not machine:
        return None
    
    # Machine 기본 정보 수정
    if name is not None:
        machine.name = name
    if manufacturer is not None:
        machine.manufacturer = manufacturer
    if client is not None:
        machine.client = client
    if description is not None:
        machine.description = description
    
    # MachineResources 수정
    if resources is not None:
        # 기존 MachineResources를 모두 삭제합니다.
        db.query(MachineResources).filter(
            MachineResources.machine_id == machine_id
        ).delete()
        
        # 새 MachineResources를 추가하고, 견적서 총액을 재계산합니다.
        total_price = 0
        for index, resource in enumerate(resources):
            machine_resource = MachineResources(
                machine_id=machine_id,
                maker_id=resource['maker_id'],
                resources_id=resource['resources_id'],
                solo_price=resource['solo_price'],
                quantity=resource['quantity'],
                order_index=index,
                display_major=resource.get("display_major"),
                display_minor=resource.get("display_minor"),
                display_model_name=resource.get("display_model_name"),
                display_maker_name=resource.get("display_maker_name"),
                display_unit=resource.get("display_unit"),
            )
            db.add(machine_resource)
            total_price += resource['solo_price'] * resource['quantity']
        
        # 견적서 총액을 업데이트합니다.
        machine.price = total_price
    
    db.commit() # 트랜잭션 커밋
    db.refresh(machine) # Machine 객체 새로고침
    return machine


def delete_machine(db: Session, machine_id: UUID) -> bool:
    """
    견적서(Machine) 및 관련된 구성 자재(MachineResources)를 삭제합니다.

    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        machine_id (UUID): 삭제할 견적서 ID.

    Returns:
        bool: 삭제 성공 시 True, 실패 시 False.
    """
    machine = db.query(Machine).filter(Machine.id == machine_id).first()
    if not machine:
        return False

    # MachineResources 먼저 삭제
    db.query(MachineResources).filter(
        MachineResources.machine_id == machine_id
    ).delete()

    # Machine 삭제
    db.delete(machine)
    db.commit()
    return True
