from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from . import crud, schemas

handler = APIRouter()

# --- Schema 정의 함수 (같은 파일 내에 있음) ---
def get_general_schema() -> dict:
    return {
        "category": { "title": "구분", "type": "string", "ratio": 1 }, # 💡 목록 조회용 스키마에 맞게 수정 필요하면 변경
        "name": { "title": "견적서명", "type": "string", "ratio": 3 },
        "client": { "title": "고객사", "type": "string", "ratio": 2 },
        "creator": { "title": "작성자", "type": "string", "ratio": 1 },
        "updated_at": { "title": "최종수정일", "type": "datetime", "format": "YYYY-MM-DD HH:mm", "ratio": 2 },
        "description": { "title": "비고", "type": "string", "ratio": 3 }
    }

def get_general_relations_schema() -> dict:
    return {
        "category": { "title": "구분", "type": "string", "ratio": 1 },
        "title": { "title": "제목/비고", "type": "string", "ratio": 3 },
        "creator": { "title": "작성자", "type": "string", "ratio": 1 },
        "updated_at": { "title": "최종수정일", "type": "datetime", "format": "YYYY-MM-DD HH:mm", "ratio": 1.5 }
    }

# --- Endpoints ---

@handler.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.GeneralResponse)
def create_general(
    general_data: schemas.GeneralCreate,
    db: Session = Depends(get_db)
):
    return crud.create_general(
        db=db,
        name=general_data.name,
        client=general_data.client,
        creator=general_data.creator,
        description=general_data.description
    )

@handler.get("")
def get_generals(
    include_schema: bool = Query(False, description="스키마 포함 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    total, generals = crud.get_generals(db, skip=skip, limit=limit)
    
    items = [
        {
            "id": g.id,
            "name": g.name,
            "client": g.client,
            "creator": g.creator,
            "created_at": g.created_at,
            "updated_at": g.updated_at,
            "description": g.description
        }
        for g in generals
    ]
    
    if include_schema:
        # 💡 [수정됨] 잘못된 import 제거하고 함수 직접 호출
        return {
            "schema": get_general_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }

@handler.get("/{general_id}", response_model=schemas.GeneralResponse)
def get_general(
    general_id: UUID,
    include_schema: bool = Query(False, description="연관 테이블 스키마 포함 여부"), # 💡 파라미터 추가
    db: Session = Depends(get_db)
):
    # 1. 데이터 조회
    result = crud.get_general_with_relations(db, general_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="General quotation not found")
    
    # 2. 스키마 포함 요청 시 추가 💡
    if include_schema:
        # Pydantic 모델에는 'schema' 필드가 없으므로, 
        # 임시로 dict로 변환해서 넣어주거나 프론트엔드에서 처리해야 함.
        # 하지만 프론트엔드 코드(loadRelationsData)를 보니 response.json()에 schema가 있기를 기대함.
        
        # 방법: Pydantic 모델을 우회하여 dict 반환 (가장 빠름)
        response_data = schemas.GeneralResponse.model_validate(result).model_dump()
        response_data['schema'] = get_general_relations_schema()
        return response_data
        
    return result

@handler.put("/{general_id}", response_model=schemas.GeneralResponse)
def update_general(
    general_id: UUID,
    general_update: schemas.GeneralUpdate,
    db: Session = Depends(get_db)
):
    updated_general = crud.update_general(
        db=db,
        general_id=general_id,
        name=general_update.name,
        client=general_update.client,
        creator=general_update.creator,
        description=general_update.description
    )
    
    if not updated_general:
        raise HTTPException(status_code=404, detail="General not found")
    
    return updated_general

@handler.delete("/{general_id}")
def delete_general(
    general_id: UUID,
    db: Session = Depends(get_db)
):
    success = crud.delete_general(db, general_id)
    if not success:
        raise HTTPException(status_code=404, detail="General not found")
    
    return {
        "message": "General deleted successfully",
        "deleted_id": str(general_id)
    }