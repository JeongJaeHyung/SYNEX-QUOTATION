# backend/api/v1/quotation/general/crud.py
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from backend.models.general import General

# ============================================================
# CRUD Functions
# ============================================================


def create_general(
    db: Session,
    name: str,
    client: str | None,
    creator: str,
    manufacturer: str,
    description: str | None,
) -> General:
    general = General(
        name=name,
        client=client,
        creator=creator,
        manufacturer=manufacturer,
        description=description,
    )
    db.add(general)
    db.commit()
    db.refresh(general)

    # 💡 견적서(일반) 생성 시 물리적 폴더 자동 생성
    import re
    from pathlib import Path

    def sanitize_folder_name(text: str) -> str:
        """폴더명에서 특수문자 제거"""
        if not text:
            return "견적서"
        return re.sub(r'[\/*?:"<>|]', "_", text).strip()

    try:
        # 기본 저장 경로 가져오기
        from backend.api.v1.export.pdf.crud import load_settings

        settings = load_settings()
        base_path = settings.get("pdfSavePath") or str(
            Path.home() / "Documents" / "JLT_견적서"
        )

        # 견적서(일반) 이름으로 폴더 생성
        safe_name = sanitize_folder_name(name)
        general_folder = Path(base_path) / safe_name
        general_folder.mkdir(parents=True, exist_ok=True)

    except Exception as e:
        # 폴더 생성 실패해도 견적서는 DB에 저장되도록 함
        print(f"Warning: Failed to create physical folder: {e}")

    return general


def get_generals(
    db: Session, skip: int = 0, limit: int = 100
) -> tuple[int, list[General]]:
    total = db.query(func.count(General.id)).scalar()
    generals = (
        db.query(General)
        .order_by(desc(General.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return total, generals


def get_general_by_id(db: Session, general_id: UUID) -> General | None:
    return db.query(General).filter(General.id == general_id).first()


def update_general(
    db: Session,
    general_id: UUID,
    name: str | None = None,
    client: str | None = None,
    creator: str | None = None,
    manufacturer: str | None = None,
    description: str | None = None,
) -> General | None:
    general = get_general_by_id(db, general_id)
    if not general:
        return None

    if name is not None:
        general.name = name
    if client is not None:
        general.client = client
    if creator is not None:
        general.creator = creator
    if manufacturer is not None:
        general.manufacturer = manufacturer
    if description is not None:
        general.description = description

    db.commit()
    db.refresh(general)
    return general


def get_general_with_relations(
    db: Session, general_id: UUID, include_relations: bool = False
) -> dict | None:
    """
    General 상세 조회
    include_relations=True이면 folders 배열 포함
    """
    general = get_general_by_id(db, general_id)
    if not general:
        return None

    result = {
        "id": general.id,
        "name": general.name,
        "client": general.client,
        "creator": general.creator,
        "manufacturer": general.manufacturer,
        "description": general.description,
        "created_at": general.created_at,
        "updated_at": general.updated_at,
    }

    # include_relations이 True일 때만 folders 배열 추가
    if include_relations:
        folder_ids = [str(folder.id) for folder in general.folders]
        result["folders"] = folder_ids

    return result


def delete_general(db: Session, general_id: UUID) -> bool:
    general = get_general_by_id(db, general_id)
    if not general:
        return False
    db.delete(general)
    db.commit()
    return True
