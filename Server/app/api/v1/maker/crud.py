# api/v1/maker/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from models.maker import Maker

# ============================================================
# Helper Functions
# ============================================================

def get_next_maker_id(db: Session) -> str:
    """
    다음 Maker ID 생성
    
    - 형식: M001, M002, M003...
    - 기존 ID 중 최대값 + 1
    """
    # 'M'로 시작하는 ID 중 최대값 조회
    max_id = db.query(func.max(Maker.id)).filter(Maker.id.like('M%')).scalar()
    
    if not max_id:
        return "M001"
    
    # 숫자 부분 추출 후 +1
    try:
        num = int(max_id[1:]) + 1
        return f"M{num:03d}"
    except:
        return "M001"


# ============================================================
# CRUD Functions
# ============================================================

def create_maker(
    db: Session,
    maker_id: Optional[str],
    name: str
) -> Maker:
    """Maker 생성"""
    # ID 자동 생성 (제공되지 않으면)
    if not maker_id:
        maker_id = get_next_maker_id(db)
    
    maker = Maker(id=maker_id, name=name)
    db.add(maker)
    db.commit()
    db.refresh(maker)
    return maker


def get_makers(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> Tuple[int, List[Maker]]:
    """Maker 목록 조회"""
    total = db.query(func.count(Maker.id)).scalar()
    makers = (
        db.query(Maker)
        .order_by(Maker.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return total, makers


def get_maker_by_id(db: Session, maker_id: str) -> Optional[Maker]:
    """Maker 단일 조회 (ID)"""
    return db.query(Maker).filter(Maker.id == maker_id).first()


def get_maker_by_name(db: Session, name: str) -> Optional[Maker]:
    """Maker 단일 조회 (이름)"""
    return db.query(Maker).filter(Maker.name == name).first()


def search_makers(
    db: Session,
    query: str,
    skip: int = 0,
    limit: int = 100
) -> Tuple[int, List[Maker]]:
    """Maker 검색 (이름 부분 매칭)"""
    query_obj = db.query(Maker).filter(Maker.name.ilike(f"%{query}%"))
    total = query_obj.count()
    makers = (
        query_obj
        .order_by(Maker.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return total, makers


def update_maker(
    db: Session,
    maker_id: str,
    name: str
) -> Optional[Maker]:
    """Maker 수정"""
    maker = get_maker_by_id(db, maker_id)
    if not maker:
        return None
    
    maker.name = name
    db.commit()
    db.refresh(maker)
    return maker


def delete_maker(db: Session, maker_id: str) -> bool:
    """Maker 삭제"""
    maker = get_maker_by_id(db, maker_id)
    if not maker:
        return False
    
    db.delete(maker)
    db.commit()
    return True