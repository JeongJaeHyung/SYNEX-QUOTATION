from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db

from . import crud, schemas

handler = APIRouter()


# --- Schema 정의 함수 ---
def get_folder_resource_schema() -> dict:
    """Folder 리소스 목록용 스키마"""
    return {
        "table_name": {"title": "유형", "type": "string", "ratio": 2},
        "title": {"title": "제목", "type": "string", "ratio": 3},
        "creator": {"title": "작성자", "type": "string", "ratio": 1},
        "updated_at": {
            "title": "최종수정일",
            "type": "datetime",
            "format": "YYYY-MM-DD HH:mm",
            "ratio": 2,
        },
        "description": {"title": "비고", "type": "string", "ratio": 2},
    }


# --- Endpoints ---


@handler.post("", status_code=status.HTTP_201_CREATED)
def create_folder(folder_data: schemas.FolderCreate, db: Session = Depends(get_db)):
    """Folder 등록"""
    # General이 존재하는지 확인
    from backend.models.general import General

    general = db.query(General).filter(General.id == folder_data.general_id).first()
    if not general:
        raise HTTPException(status_code=404, detail="General not found")

    # 동일한 제목의 Folder가 이미 있는지 확인 (선택적)
    existing = (
        db.query(crud.Folder)
        .filter(
            crud.Folder.general_id == folder_data.general_id,
            crud.Folder.title == folder_data.title,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409, detail="Folder with same title already exists"
        )

    folder = crud.create_folder(
        db=db, general_id=folder_data.general_id, title=folder_data.title
    )

    return {"id": folder.id, "title": folder.title, "created_at": folder.created_at}


@handler.get("/{folder_id}")
def get_folder(
    folder_id: UUID,
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    db: Session = Depends(get_db),
):
    """Folder 조회 (리소스 포함)"""
    result = crud.get_folder_with_resources(db, folder_id)

    if not result:
        raise HTTPException(status_code=404, detail="Folder not found")

    # include_schema=True일 때 스키마 추가
    if include_schema:
        result["schema"] = get_folder_resource_schema()

    return result


@handler.put("/{folder_id}")
def update_folder(
    folder_id: UUID, folder_update: schemas.FolderUpdate, db: Session = Depends(get_db)
):
    """Folder 수정"""
    updated_folder = crud.update_folder(
        db=db, folder_id=folder_id, title=folder_update.title
    )

    if not updated_folder:
        raise HTTPException(status_code=404, detail="Folder not found")

    return {
        "id": updated_folder.id,
        "title": updated_folder.title,
        "updated_at": updated_folder.updated_at,
        "message": "Folder updated successfully",
    }


@handler.delete("/{folder_id}")
def delete_folder(folder_id: UUID, db: Session = Depends(get_db)):
    """Folder 삭제"""
    success = crud.delete_folder(db, folder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Folder not found")

    return {"message": "Folder deleted successfully", "deleted_id": str(folder_id)}
