from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from uuid import UUID
from typing import List, Optional, Tuple
from backend.models.general import General

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
    return db.query(General).filter(General.id == general_id).first()

def update_general(
    db: Session,
    general_id: UUID,
    name: Optional[str] = None,
    client: Optional[str] = None,
    creator: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[General]:
    general = get_general_by_id(db, general_id)
    if not general:
        return None
    
    if name is not None: general.name = name
    if client is not None: general.client = client
    if creator is not None: general.creator = creator
    if description is not None: general.description = description
    
    db.commit()
    db.refresh(general)
    return general

def get_general_with_relations(db: Session, general_id: UUID) -> Optional[dict]:
    """
    General 상세 조회 (연관 테이블 포함)
    PriceCompare, Quotation, Detailed 데이터를 통합하여 related_documents로 반환
    """
    general = get_general_by_id(db, general_id)
    if not general:
        return None
    
    # 통합 목록 생성
    related_docs = []
    
    # 1. PriceCompare (비교 견적)
    if general.price_compares:
        for pc in general.price_compares:
            related_docs.append({
                "id": pc.id,
                "category": "비교 견적서",
                "title": pc.description if pc.description else "내정가 비교", # 제목이 없으면 비고 사용
                "creator": pc.creator,
                "updated_at": pc.updated_at
            })
    
    # 2. Quotation (견적서 갑지) - 모델이 있다면
    if hasattr(general, 'quotations') and general.quotations:
        for q in general.quotations:
            related_docs.append({
                "id": q.id,
                "category": "견적서(갑)",
                "title": q.title,
                "creator": q.creator,
                "updated_at": q.updated_at
            })

    # 3. Detailed (상세 견적) - 모델이 있다면
    if hasattr(general, 'detaileds') and general.detaileds:
        for d in general.detaileds:
            related_docs.append({
                "id": d.id,
                "category": "상세 견적서",
                "title": d.description if d.description else "상세 내역",
                "creator": d.creator,
                "updated_at": d.updated_at
            })
    
    # 최신 수정순 정렬
    related_docs.sort(key=lambda x: x['updated_at'], reverse=True)
    
    # Pydantic Schema(GeneralResponse) 구조에 맞게 Dict 리턴
    return {
        "id": general.id,
        "name": general.name,
        "client": general.client,
        "creator": general.creator,
        "description": general.description,
        "created_at": general.created_at,
        "updated_at": general.updated_at,
        "related_documents": related_docs  # 💡 여기가 핵심
    }

def delete_general(db: Session, general_id: UUID) -> bool:
    general = get_general_by_id(db, general_id)
    if not general:
        return False
    db.delete(general)
    db.commit()
    return True