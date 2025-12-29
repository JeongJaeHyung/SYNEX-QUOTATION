# backend/api/v1/quotation/folder/crud.py
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.folder import Folder
from backend.models.general import General


def create_folder(db: Session, general_id: UUID, title: str) -> Folder:
    """Folder 생성"""
    folder = Folder(general_id=general_id, title=title)
    db.add(folder)
    db.commit()
    db.refresh(folder)

    # 💡 폴더 생성 시 상위 견적서(일반) 폴더 하위에 물리적 폴더 생성
    import re
    from pathlib import Path

    def sanitize_folder_name(text: str) -> str:
        """폴더명에서 특수문자 제거"""
        if not text:
            return "폴더"
        return re.sub(r'[\/*?:"<>|]', "_", text).strip()

    try:
        # 기본 저장 경로 가져오기
        from backend.api.v1.export.pdf.crud import load_settings

        settings = load_settings()
        base_path = settings.get("pdfSavePath") or str(
            Path.home() / "Documents" / "JLT_견적서"
        )

        # 상위 견적서(일반) 정보 가져오기
        general = db.query(General).filter(General.id == general_id).first()
        if general:
            safe_general_name = sanitize_folder_name(general.name)
            safe_folder_title = sanitize_folder_name(title)

            # 견적서(일반)/폴더명 경로로 폴더 생성
            folder_path = Path(base_path) / safe_general_name / safe_folder_title
            folder_path.mkdir(parents=True, exist_ok=True)

            # Excel 및 PDF 하위 폴더도 미리 생성
            (folder_path / "Excel").mkdir(exist_ok=True)
            (folder_path / "PDF").mkdir(exist_ok=True)

    except Exception as e:
        # 폴더 생성 실패해도 DB 레코드는 저장되도록 함
        print(f"Warning: Failed to create physical folder: {e}")

    return folder


def get_folder_by_id(db: Session, folder_id: UUID) -> Folder | None:
    """Folder 단일 조회"""
    return db.query(Folder).filter(Folder.id == folder_id).first()


def get_folder_with_resources(db: Session, folder_id: UUID) -> dict | None:
    """
    Folder 상세 조회 (리소스 포함)
    각 폴더당 PriceCompare, Detailed, Header는 최대 1개씩만 존재
    resources 배열로 반환
    """
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return None

    resources = []

    # 1. PriceCompare (내정가 비교) - 최대 1개
    if folder.price_compares:
        pc = folder.price_compares[0]  # 첫 번째 항목만 사용
        resources.append(
            {
                "table_name": "내정가 비교",
                "id": pc.id,
                "title": pc.title if pc.title else "내정가견적비교서",
                "creator": pc.creator,
                "updated_at": pc.updated_at,
                "description": pc.description,
            }
        )

    # 2. Detailed (견적서(을지)) - 최대 1개
    if folder.detaileds:
        d = folder.detaileds[0]  # 첫 번째 항목만 사용
        resources.append(
            {
                "table_name": "견적서(을지)",
                "id": d.id,
                "title": d.title if d.title else "상세 견적",
                "creator": d.creator,
                "updated_at": d.updated_at,
                "description": d.description,
            }
        )

    # 3. Header (견적서) - 최대 1개
    if folder.headers:
        h = folder.headers[0]  # 첫 번째 항목만 사용
        resources.append(
            {
                "table_name": "견적서",
                "id": h.id,
                "title": h.title,
                "creator": h.creator,
                "updated_at": h.updated_at,
                "description": h.description_1 if hasattr(h, "description_1") else None,
            }
        )

    # 최신 수정순 정렬
    resources.sort(key=lambda x: x["updated_at"], reverse=True)

    # 💡 General 정보도 함께 반환 (PDF 저장 속도 개선)
    general_name = None
    if folder.general:
        general_name = folder.general.name

    return {
        "id": folder.id,
        "general_id": folder.general_id,
        "general_name": general_name,  # 추가
        "title": folder.title,
        "updated_at": folder.updated_at,
        "resource_count": len(resources),
        "resources": resources,
    }


def update_folder(
    db: Session, folder_id: UUID, title: str | None = None
) -> Folder | None:
    """Folder 수정"""
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return None

    if title is not None:
        folder.title = title

    db.commit()
    db.refresh(folder)
    return folder


def delete_folder(db: Session, folder_id: UUID) -> bool:
    """Folder 삭제"""
    folder = get_folder_by_id(db, folder_id)
    if not folder:
        return False
    db.delete(folder)
    db.commit()
    return True


def get_folder_resources(db: Session, folder_id: UUID) -> list[dict]:
    """
    Folder의 리소스 목록 반환 (Excel/PDF 통합용)
    """
    folder_data = get_folder_with_resources(db, folder_id)
    if not folder_data:
        return []
    return folder_data.get("resources", [])
