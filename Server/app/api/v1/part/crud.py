# api/v1/part/crud.py
#
# 부품(Resources) 데이터베이스 작업을 위한 CRUD(Create, Read, Update, Delete) 함수를 정의합니다.
# - 부품 ID 생성, 부품 및 인증 정보 생성/조회/검색/수정/삭제 기능을 제공합니다.
#

from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위함
from sqlalchemy import and_, or_, func # SQLAlchemy AND, OR 조건 및 함수 사용을 위함
from typing import List, Tuple, Optional # 타입 힌트
from models.resources import Resources # Resources 모델 임포트
from models.maker import Maker # Maker 모델 임포트
from models.certification import Certification # Certification 모델 임포트
from .schemas import PartsFilter # 부품 필터링 스키마 임포트

# ============================================================
# 헬퍼 함수
# ============================================================

def get_maker_by_name(db: Session, maker_name: str) -> Optional[Maker]:
    """
    제조사 이름을 사용하여 데이터베이스에서 제조사(Maker) 정보를 조회합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        maker_name (str): 조회할 제조사 이름.
        
    Returns:
        Optional[Maker]: 조회된 Maker 객체, 없으면 None.
    """
    return db.query(Maker).filter(Maker.name == maker_name).first()


def get_next_parts_id(db: Session, maker_id: str) -> str:
    """
    지정된 제조사(Maker)에 대한 다음 부품(Parts) ID를 생성합니다.
    - 형식: 6자리 숫자 (예: "000001", "000002")
    - 각 제조사별로 독립적으로 ID가 증가합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        maker_id (str): ID를 생성할 제조사의 ID.
        
    Returns:
        str: 새로 생성된 6자리 부품 ID.
    """
    # 해당 제조사의 기존 부품 중 최대 ID를 조회합니다.
    max_id = db.query(func.max(Resources.id)).filter(
        Resources.maker_id == maker_id
    ).scalar()
    
    if max_id is None:
        return "000001" # 해당 제조사의 부품이 없으면 "000001" 반환
    
    # 최대 ID의 숫자 부분을 추출하여 1을 더하고, 6자리 문자열로 포맷팅합니다.
    try:
        next_num = int(max_id) + 1
        return f"{next_num:06d}"
    except (ValueError, TypeError): # ID가 숫자로 변환 불가능한 경우 (예외 처리)
        return "000001" # 오류 발생 시 기본값 반환


# ============================================================
# CRUD 함수
# ============================================================

def create_parts(
    db: Session,
    parts_id: str, # 생성할 부품 ID
    maker_id: str, # 부품의 제조사 ID
    major: str,    # 대분류 (Unit)
    minor: str,    # 중분류 (품목)
    name: str,     # 모델명/규격
    unit: str,     # 단위
    solo_price: int, # 단가
    display_order: Optional[int] = None, # 표시 순서 (지정 없으면 자동 할당)
    ul: bool = False, # UL 인증 여부
    ce: bool = False, # CE 인증 여부
    kc: bool = False, # KC 인증 여부
    etc: Optional[str] = None # 기타 인증/비고
) -> Resources:
    """
    새로운 부품(Resources)을 생성하고 관련 인증 정보(Certification)를 함께 저장합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        (위에 정의된 인자들)
        
    Returns:
        Resources: 생성된 Resources 객체.
    """
    # display_order가 지정되지 않으면 현재 최대 display_order에 1을 더하여 할당합니다.
    if display_order is None:
        max_order = db.query(func.max(Resources.display_order)).scalar()
        display_order = 0 if max_order is None else int(max_order) + 1

    # Resources 모델 인스턴스 생성
    resource = Resources(
        id=parts_id,
        maker_id=maker_id,
        major=major,
        minor=minor,
        name=name,
        unit=unit,
        solo_price=solo_price,
        display_order=display_order,
    )
    db.add(resource) # 세션에 자원 객체 추가
    db.flush() # ID 할당 및 관계 설정을 위해 플러시 (아직 커밋은 아님)
    
    # Certification 모델 인스턴스 생성 및 연결
    certification = Certification(
        resources_id=parts_id,
        maker_id=maker_id,
        ul=ul,
        ce=ce,
        kc=kc,
        etc=etc
    )
    db.add(certification) # 세션에 인증 객체 추가
    
    db.commit() # 트랜잭션 커밋 (DB에 변경사항 반영)
    db.refresh(resource) # 커밋된 자원 객체를 최신 상태로 새로고침
    return resource


def get_parts_by_id(db: Session, parts_id: str, maker_id: str) -> Optional[Resources]:
    """
    부품 ID와 제조사 ID(복합 Primary Key)를 사용하여 단일 부품 정보를 조회합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        parts_id (str): 조회할 부품 ID.
        maker_id (str): 조회할 제조사 ID.
        
    Returns:
        Optional[Resources]: 조회된 Resources 객체, 없으면 None.
    """
    return db.query(Resources).filter(
        and_(Resources.id == parts_id, Resources.maker_id == maker_id) # 복합 PK 조건
    ).first()


def get_parts_list(
    db: Session,
    filters: PartsFilter, # 검색 및 필터링 조건을 담은 Pydantic 객체
    skip: int = 0, # 조회 시작 지점 (OFFSET)
    limit: int = 100 # 조회할 최대 개수 (LIMIT)
) -> Tuple[List[Resources], int]:
    """
    데이터베이스에서 부품(Resources) 목록을 조회하고, 다양한 필터링 및 페이징 기능을 지원합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        filters (PartsFilter): ID, 제조사 ID, 이름, 단위, 가격 범위, 대분류, 중분류, 인증 여부 등 필터링 조건.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        
    Returns:
        Tuple[List[Resources], int]: (부품 객체 리스트, 총 필터링된 개수).
    """
    query = db.query(Resources).join(Resources.maker) # Resources와 Maker를 조인하여 제조사 이름 필터링에 대비
    
    # --- 필터링 조건 적용 ---
    if filters.id is not None:
        query = query.filter(Resources.id.ilike(f"%{filters.id}%"))
    if filters.maker_id is not None:
        query = query.filter(Resources.maker_id == filters.maker_id)
    if filters.name is not None:
        query = query.filter(Resources.name.ilike(f"%{filters.name}%"))
    if filters.unit is not None:
        query = query.filter(Resources.unit == filters.unit)
    if filters.min_price is not None:
        query = query.filter(Resources.solo_price >= filters.min_price)
    if filters.max_price is not None:
        query = query.filter(Resources.solo_price <= filters.max_price)
    if filters.major is not None:
        query = query.filter(Resources.major.ilike(f"%{filters.major}%"))
    if filters.minor is not None:
        query = query.filter(Resources.minor.ilike(f"%{filters.minor}%"))
    
    # Certification 필터 (Certification 테이블과의 조인이 필요)
    if filters.ul is not None or filters.ce is not None or filters.kc is not None:
        query = query.join(Resources.certification) # Certification 테이블과 조인
        if filters.ul is not None:
            query = query.filter(Certification.ul == filters.ul)
        if filters.ce is not None:
            query = query.filter(Certification.ce == filters.ce)
        if filters.kc is not None:
            query = query.filter(Certification.kc == filters.kc)
    
    total = query.count() # 필터링된 결과의 총 개수

    # --- 정렬 및 페이징 적용 ---
    parts_list = query.order_by(Resources.maker_id.asc(), Resources.id.asc()).offset(skip).limit(limit).all() # 품목코드(maker_id + id) 순서로 정렬

    return parts_list, total


def search_parts(
    db: Session,
    query: str, # 검색어
    search_fields: List[str], # 검색할 필드 목록 (예: 'name', 'maker_name')
    skip: int = 0,
    limit: int = 20
) -> Tuple[List[Resources], int]:
    """
    여러 필드에 걸쳐 부품(Resources)을 검색합니다 (OR 조건).
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        query (str): 검색할 문자열.
        search_fields (List[str]): 검색을 수행할 필드 목록 (예: ['name', 'maker_name', 'major']).
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        
    Returns:
        Tuple[List[Resources], int]: (검색된 Resources 객체 리스트, 총 검색 결과 개수).
    """
    query_obj = db.query(Resources).join(Resources.maker) # Maker 정보를 함께 검색하기 위해 조인
    
    conditions = [] # OR 조건들을 담을 리스트
    
    # search_fields에 따라 동적으로 검색 조건을 추가합니다.
    if 'name' in search_fields:
        conditions.append(Resources.name.ilike(f"%{query}%"))
    if 'id' in search_fields:
        conditions.append(Resources.id.ilike(f"%{query}%"))
    if 'maker_name' in search_fields:
        conditions.append(Maker.name.ilike(f"%{query}%"))
    if 'major' in search_fields:
        conditions.append(Resources.major.ilike(f"%{query}%"))
    if 'minor' in search_fields:
        conditions.append(Resources.minor.ilike(f"%{query}%"))
    
    if conditions:
        query_obj = query_obj.filter(or_(*conditions)) # OR 조건 적용
    
    total = query_obj.count() # 검색 결과 총 개수

    parts_list = query_obj.order_by(Resources.maker_id.asc(), Resources.id.asc()).offset(skip).limit(limit).all() # 품목코드 순서로 정렬

    return parts_list, total


def update_parts(
    db: Session,
    parts_id: str,
    maker_id: str,
    major: Optional[str] = None, # 대분류
    minor: Optional[str] = None, # 중분류
    name: Optional[str] = None, # 모델명/규격
    unit: Optional[str] = None, # 단위
    solo_price: Optional[int] = None, # 단가
    ul: Optional[bool] = None, # UL 인증 여부
    ce: Optional[bool] = None, # CE 인증 여부
    kc: Optional[bool] = None, # KC 인증 여부
    etc: Optional[str] = None # 기타 인증/비고
) -> Optional[Resources]:
    """
    기존 부품(Resources) 및 관련 인증 정보(Certification)를 업데이트합니다.
    부분 업데이트를 지원하며, 제공된 필드만 업데이트됩니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        (위에 정의된 인자들)
        
    Returns:
        Optional[Resources]: 업데이트된 Resources 객체, 없으면 None (부품을 찾지 못한 경우).
    """
    resource = get_parts_by_id(db, parts_id, maker_id) # 복합 PK로 부품 조회
    if not resource:
        return None
    
    # Resources 테이블 업데이트
    if major is not None:
        resource.major = major
    if minor is not None:
        resource.minor = minor
    if name is not None:
        resource.name = name
    if unit is not None:
        resource.unit = unit
    if solo_price is not None:
        resource.solo_price = solo_price
    
    # Certification 테이블 업데이트 (Certification 객체가 존재하는 경우에만)
    if resource.certification:
        if ul is not None:
            resource.certification.ul = ul
        if ce is not None:
            resource.certification.ce = ce
        if kc is not None:
            resource.certification.kc = kc
        if etc is not None:
            resource.certification.etc = etc
    
    db.commit() # 트랜잭션 커밋
    db.refresh(resource) # 객체 새로고침
    return resource


def delete_parts(db: Session, parts_id: str, maker_id: str) -> bool:
    """
    부품(Resources) 및 관련 인증 정보(Certification)를 데이터베이스에서 삭제합니다.
    - Resources 모델에 CASCADE 설정이 없으므로 Certification이 먼저 삭제되어야 하지만,
      Resources 테이블 정의 시 Certification과의 관계에 `cascade="all, delete-orphan"`이
      설정되어 있거나, Foreign Key 제약 조건에 `ON DELETE CASCADE`가 설정되어 있으면 자동으로 함께 삭제됩니다.
      현재 Resources 모델에 관계 설정은 없지만, Certification 테이블에 ForeignKeyConstraint가 정의되어 있습니다.
      (참고: `certification` 모델에 `ForeignKeyConstraint`가 있고, Resources에 `relationship` 정의에 `cascade`가 없으므로 수동 삭제 또는 DB 설정 필요)
      -> `certification` 모델에 `ForeignKeyConstraint`에 `ondelete='CASCADE'`가 명시되어 있지 않으면
      Resources 삭제 전에 Certification을 먼저 삭제해야 에러가 나지 않습니다.
      현재는 Certification이 Resources를 FK로 참조하고 있어, Resources 삭제 시 Certification은 자동으로
      삭제되지 않을 수 있으므로 주의해야 합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        parts_id (str): 삭제할 부품 ID.
        maker_id (str): 삭제할 제조사 ID.
        
    Returns:
        bool: 삭제 성공 시 True, 실패 시 False.
    """
    resource = get_parts_by_id(db, parts_id, maker_id) # 부품 조회
    if not resource:
        return False
    
    # Certification이 먼저 삭제되어야 Resources를 삭제할 수 있음 (FK 제약조건 때문에)
    # 현재 모델 정의에서는 Resource 삭제 시 Certification이 자동 삭제되지 않으므로, 명시적으로 삭제 로직이 필요.
    # 하지만 실제 DB 스키마에 ON DELETE CASCADE가 걸려있다면 이 로직은 불필요.
    # 여기서는 ORM 모델의 관계 정의에 따라 처리됩니다.
    # resource.certification이 있으면 db.delete(resource.certification) 필요.
    # 하지만 resources 모델의 relationship에 cascade="all, delete-orphan"이 없으므로 직접 처리해야 할 수 있음.
    # 현재 Certification 모델의 __table_args__에 ondelete='CASCADE'가 없으므로 db.delete(resource.certification)을 먼저 해야 함.

    # FIXME: Certification이 먼저 삭제되어야 함.
    if resource.certification:
        db.delete(resource.certification)
        db.commit() # Certification 삭제 커밋

    db.delete(resource) # Resources 삭제
    db.commit() # 트랜잭션 커밋
    return True