# api/v1/general/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from uuid import UUID
from typing import List, Optional, Tuple
from models.general import General

# ============================================================
# CRUD Functions
# ============================================================

def create_general(
    db: Session,
    name: str,
    client: Optional[str],
    creator: str,
    description: Optional[str]
) -> General:
    """General 생성"""
    general = General(
        name=name,
        client=client,
        creator=creator,
        description=description
    )
    db.add(general)
    db.commit()
    db.refresh(general)
    return general


def get_generals(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> Tuple[int, List[General]]:
    """General 목록 조회 (created_at DESC)"""
    total = db.query(func.count(General.id)).scalar()
    
    generals = (
        db.query(General)
        .order_by(desc(General.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return total, generals


def get_general_by_id(db: Session, general_id: UUID) -> Optional[General]:
    """General 단일 조회"""
    return db.query(General).filter(General.id == general_id).first()


def update_general(
    db: Session,
    general_id: UUID,
    name: Optional[str] = None,
    client: Optional[str] = None,
    creator: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[General]:
    """General 수정 (부분 수정)"""
    general = get_general_by_id(db, general_id)
    if not general:
        return None
    
    # 수정할 필드만 업데이트
    if name is not None:
        general.name = name
    if client is not None:
        general.client = client
    if creator is not None:
        general.creator = creator
    if description is not None:
        general.description = description
    
    db.commit()
    db.refresh(general)
    return general


def get_general_with_relations(db: Session, general_id: UUID) -> Optional[dict]:
    """
    General 상세 조회 (연관 테이블 포함)
    
    반환 필드: table_name, id, creator, updated_at, description
    """
    general = get_general_by_id(db, general_id)
    if not general:
        return None
    
    # 통합 목록 (모든 연관 테이블)
    items = []
    
    # PriceCompare 목록
    for pc in general.price_compares:
        items.append({
            "table_name": "가격 비교",
            "id": str(pc.id),
            "creator": pc.creator,
            "updated_at": pc.updated_at,
            "description": pc.description
        })
    
    # Detailed 목록
    for d in general.detaileds:
        items.append({
            "table_name": "상세 견적",
            "id": str(d.id),
            "creator": d.creator,
            "updated_at": d.updated_at,
            "description": d.description
        })
    
    # Quotation 목록
    for q in general.quotations:
        items.append({
            "table_name": "견적서",
            "id": str(q.id),
            "creator": q.creator,
            "updated_at": q.updated_at,
            "description": q.description_1  # description_1 사용
        })
    
    return {
        "general": {
            "id": general.id,
            "name": general.name,
            "client": general.client,
            "creator": general.creator,
            "description": general.description,
            "created_at": general.created_at,
            "updated_at": general.updated_at
        },
        "items": items
    }


def delete_general(db: Session, general_id: UUID) -> bool:
    """General 삭제 (CASCADE로 연관 데이터 자동 삭제)"""
    general = get_general_by_id(db, general_id)
    if not general:
        return False
    
    db.delete(general)
    db.commit()
    return True