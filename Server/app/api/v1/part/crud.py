# api/v1/parts/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Tuple, Optional, Dict, Any
from models.resources import Resources
from models.maker import Maker
from models.category import Category
from models.certification import Certification

# ============================================================
# Helper Functions
# ============================================================

def get_maker_by_name(db: Session, maker_name: str) -> Optional[Maker]:
    """제조사명으로 Maker 조회"""
    return db.query(Maker).filter(Maker.name == maker_name).first()


def get_category_by_major_minor(db: Session, major: str, minor: str) -> Optional[Category]:
    """대분류+소분류로 Category 조회"""
    return db.query(Category).filter(
        and_(Category.major == major, Category.minor == minor)
    ).first()


def get_next_parts_id(db: Session, maker_id: str) -> str:
    """
    제조사별 다음 Parts ID 생성
    
    - 형식: 6자리 숫자 (000001, 000002, ...)
    - 제조사별 독립적으로 증가
    """
    # 해당 제조사의 최대 ID 조회
    max_id = db.query(func.max(Resources.id)).filter(
        Resources.maker_id == maker_id
    ).scalar()
    
    if max_id is None:
        return "000001"
    
    # 숫자로 변환 후 +1, 다시 6자리 문자열로
    next_num = int(max_id) + 1
    return f"{next_num:06d}"


# ============================================================
# CRUD Functions
# ============================================================

def create_parts(
    db: Session,
    parts_id: str,
    maker_id: str,
    category_id: int,
    name: str,
    unit: str,
    solo_price: int,
    ul: bool = False,
    ce: bool = False,
    kc: bool = False,
    etc: Optional[str] = None
) -> Resources:
    """
    Parts 생성
    
    - Resources 생성
    - Certification 생성 (별도 테이블)
    """
    # Resources 생성
    resource = Resources(
        id=parts_id,
        maker_id=maker_id,
        category_id=category_id,
        name=name,
        unit=unit,
        solo_price=solo_price
    )
    db.add(resource)
    db.flush()  # ID 할당을 위해 flush
    
    # Certification 생성
    certification = Certification(
        resources_id=parts_id,
        maker_id=maker_id,
        ul=ul,
        ce=ce,
        kc=kc,
        etc=etc
    )
    db.add(certification)
    
    db.commit()
    db.refresh(resource)
    return resource


def get_parts_by_id(db: Session, parts_id: str, maker_id: str) -> Optional[Resources]:
    """Parts 단일 조회 (복합 PK)"""
    return db.query(Resources).filter(
        and_(Resources.id == parts_id, Resources.maker_id == maker_id)
    ).first()


def get_parts_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> Tuple[int, List[Resources]]:
    """
    Parts 목록 조회 + 필터링
    
    - 11개 필터 파라미터 지원
    - updated_at DESC 정렬
    """
    query = db.query(Resources).join(Resources.maker).join(Resources.category)
    
    # 필터 적용
    if filters:
        if 'id' in filters:
            query = query.filter(Resources.id.ilike(f"%{filters['id']}%"))
        if 'maker_id' in filters:
            query = query.filter(Resources.maker_id == filters['maker_id'])
        if 'name' in filters:
            query = query.filter(Resources.name.ilike(f"%{filters['name']}%"))
        if 'unit' in filters:
            query = query.filter(Resources.unit == filters['unit'])
        if 'min_price' in filters:
            query = query.filter(Resources.solo_price >= filters['min_price'])
        if 'max_price' in filters:
            query = query.filter(Resources.solo_price <= filters['max_price'])
        if 'major' in filters:
            query = query.filter(Category.major.ilike(f"%{filters['major']}%"))
        if 'minor' in filters:
            query = query.filter(Category.minor.ilike(f"%{filters['minor']}%"))
        
        # Certification 필터 (JOIN 필요)
        if 'ul' in filters or 'ce' in filters or 'kc' in filters:
            query = query.join(Resources.certification)
            if 'ul' in filters:
                query = query.filter(Certification.ul == filters['ul'])
            if 'ce' in filters:
                query = query.filter(Certification.ce == filters['ce'])
            if 'kc' in filters:
                query = query.filter(Certification.kc == filters['kc'])
    
    # Total count
    total = query.count()
    
    # 정렬 + 페이징
    parts_list = query.order_by(Resources.updated_at.desc()).offset(skip).limit(limit).all()
    
    return total, parts_list


def search_parts(
    db: Session,
    query: str,
    search_fields: List[str],
    skip: int = 0,
    limit: int = 20
) -> Tuple[int, List[Resources]]:
    """
    Parts 검색 (여러 필드 OR 조건)
    
    - search_fields: name, id, maker_name, major, minor
    """
    query_obj = db.query(Resources).join(Resources.maker).join(Resources.category)
    
    conditions = []
    
    if 'name' in search_fields:
        conditions.append(Resources.name.ilike(f"%{query}%"))
    if 'id' in search_fields:
        conditions.append(Resources.id.ilike(f"%{query}%"))
    if 'maker_name' in search_fields:
        conditions.append(Maker.name.ilike(f"%{query}%"))
    if 'major' in search_fields:
        conditions.append(Category.major.ilike(f"%{query}%"))
    if 'minor' in search_fields:
        conditions.append(Category.minor.ilike(f"%{query}%"))
    
    if conditions:
        query_obj = query_obj.filter(or_(*conditions))
    
    # Total count
    total = query_obj.count()
    
    # 정렬 + 페이징
    parts_list = query_obj.order_by(Resources.updated_at.desc()).offset(skip).limit(limit).all()
    
    return total, parts_list


def update_parts(
    db: Session,
    parts_id: str,
    maker_id: str,
    category_id: Optional[int] = None,
    name: Optional[str] = None,
    unit: Optional[str] = None,
    solo_price: Optional[int] = None,
    ul: Optional[bool] = None,
    ce: Optional[bool] = None,
    kc: Optional[bool] = None,
    etc: Optional[str] = None
) -> Optional[Resources]:
    """
    Parts 수정 (부분 수정)
    
    - Resources 수정
    - Certification 수정
    """
    # Resources 조회
    resource = get_parts_by_id(db, parts_id, maker_id)
    if not resource:
        return None
    
    # Resources 업데이트
    if category_id is not None:
        resource.category_id = category_id
    if name is not None:
        resource.name = name
    if unit is not None:
        resource.unit = unit
    if solo_price is not None:
        resource.solo_price = solo_price
    
    # Certification 업데이트
    if resource.certification:
        if ul is not None:
            resource.certification.ul = ul
        if ce is not None:
            resource.certification.ce = ce
        if kc is not None:
            resource.certification.kc = kc
        if etc is not None:
            resource.certification.etc = etc
    
    db.commit()
    db.refresh(resource)
    return resource


def delete_parts(db: Session, parts_id: str, maker_id: str) -> bool:
    """
    Parts 삭제
    
    - CASCADE로 Certification도 자동 삭제
    """
    resource = get_parts_by_id(db, parts_id, maker_id)
    if not resource:
        return False
    
    db.delete(resource)
    db.commit()
    return True