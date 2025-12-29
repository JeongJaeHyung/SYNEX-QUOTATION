# api/v1/maker/handler.py
#
# 제조사(Maker) 관련 API 엔드포인트를 정의합니다.
# - 제조사 생성, 목록 조회, 검색, 상세 조회, 수정, 삭제 API를 제공합니다.
#

from typing import List, Optional  # 타입 힌트 (선택적 인자, 리스트)

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)  # FastAPI 라우터, 의존성 주입, HTTP 예외 처리, 쿼리 파라미터
from sqlalchemy.orm import Session  # 데이터베이스 세션 관리를 위함

from backend.database import get_db

from . import crud, schemas  # Maker CRUD 함수 및 스키마(DTO) 임포트

# API 라우터 인스턴스 생성
handler = APIRouter()

# ============================================================
# 스키마 생성 헬퍼 함수
# ============================================================


def get_maker_schema() -> dict:
    """
    Maker 응답 DTO의 스키마 정의를 반환합니다.
    - 프론트엔드에서 테이블 헤더 및 컬럼 속성을 동적으로 생성할 때 사용될 수 있습니다.

    Returns:
        dict: Maker 스키마 정의 딕셔너리.
    """
    return {
        "id": {
            "title": "제조사코드",  # 테이블 헤더에 표시될 이름
            "type": "string",
            "ratio": 1,  # 컬럼 너비 비율
        },
        "name": {"title": "제조사명", "type": "string", "ratio": 3},
        "created_at": {
            "title": "등록일",
            "type": "datetime",
            "format": "YYYY-MM-DD HH:mm",
            "ratio": 2,
        },
    }


# ============================================================
# Maker Endpoints (제조사 관련 API)
# ============================================================


@handler.post("", status_code=201)
def create_maker(
    maker_data: schemas.MakerCreate,  # 요청 바디는 MakerCreate 스키마를 따름
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):
    """
    새로운 제조사(Maker)를 등록하는 API 엔드포인트입니다.
    - 제조사 이름 또는 ID의 중복을 확인한 후 제조사를 생성합니다.
    - ID가 제공되지 않으면 자동으로 생성됩니다.

    Args:
        maker_data (schemas.MakerCreate): 등록할 제조사 정보를 담은 DTO.
        db (Session): SQLAlchemy 데이터베이스 세션.

    Returns:
        dict: 생성된 제조사 정보와 성공 메시지.

    Raises:
        HTTPException: 이름 또는 ID가 중복될 경우 409 Conflict.
    """
    # --- 이름 중복 체크 ---
    existing = crud.get_maker_by_name(db, maker_data.name)
    if existing:
        raise HTTPException(
            status_code=409, detail=f"제조사 '{maker_data.name}'이(가) 이미 존재합니다."
        )

    # --- ID 중복 체크 (ID가 요청에 포함된 경우) ---
    if maker_data.id:
        existing_id = crud.get_maker_by_id(db, maker_data.id)
        if existing_id:
            raise HTTPException(
                status_code=409,
                detail=f"제조사 ID '{maker_data.id}'이(가) 이미 존재합니다.",
            )

    # --- Maker 생성 ---
    maker = crud.create_maker(db, maker_data.name, maker_data.id)

    # 생성된 제조사 정보를 포함하는 응답 반환
    return {
        "id": maker.id,
        "name": maker.name,
        "created_at": maker.created_at,
        "message": "제조사가 성공적으로 생성되었습니다.",
    }


@handler.get("")
def get_makers(
    include_schema: bool = Query(
        False, description="응답에 스키마 정의를 포함할지 여부"
    ),
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="가져올 최대 레코드 수"),
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):
    """
    모든 제조사 목록을 조회하는 API 엔드포인트입니다.
    - 페이징 및 스키마 포함 옵션을 지원합니다.

    Args:
        include_schema (bool): 응답에 스키마 정의를 포함할지 여부.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        db (Session): SQLAlchemy 데이터베이스 세션.

    Returns:
        dict: 제조사 목록과 페이징 정보를 담은 딕셔너리. 스키마 포함 시 스키마 정의도 포함.
    """
    total, makers = crud.get_makers(db, skip=skip, limit=limit)

    # Maker 객체 리스트를 DTO 형식의 딕셔너리 리스트로 변환합니다.
    items = [
        {
            "id": m.id,
            "name": m.name,
            "created_at": m.created_at,  # 생성일시 포함
        }
        for m in makers
    ]

    # 스키마 포함 옵션에 따라 응답을 구성합니다.
    if include_schema:
        return {
            "schema": get_maker_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit,
        }

    return {"total": total, "items": items, "skip": skip, "limit": limit}


@handler.get("/search")
def search_makers(
    query: str = Query(..., min_length=1, description="제조사 이름에서 검색할 문자열"),
    include_schema: bool = Query(
        False, description="응답에 스키마 정의를 포함할지 여부"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):
    """
    검색어를 사용하여 제조사 목록을 조회하는 API 엔드포인트입니다.
    - 제조사 이름에 대한 부분 매칭을 수행합니다.
    - 페이징 및 스키마 포함 옵션을 지원합니다.

    Args:
        query (str): 제조사 이름에서 검색할 문자열 (최소 1자).
        include_schema (bool): 응답에 스키마 정의를 포함할지 여부.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        db (Session): SQLAlchemy 데이터베이스 세션.

    Returns:
        dict: 검색된 제조사 목록과 페이징 정보를 담은 딕셔너리.

    Raises:
        HTTPException: 쿼리가 너무 짧을 경우 (FastAPI의 Query 검증이 처리).
    """
    total, makers = crud.search_makers(db, query, skip=skip, limit=limit)

    # Maker 객체 리스트를 DTO 형식의 딕셔너리 리스트로 변환합니다.
    items = [{"id": m.id, "name": m.name, "created_at": m.created_at} for m in makers]

    # 스키마 포함 옵션에 따라 응답을 구성합니다.
    if include_schema:
        return {
            "schema": get_maker_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit,
        }

    return {"total": total, "items": items, "skip": skip, "limit": limit}


@handler.get("/{maker_id}")
def get_maker(
    maker_id: str,  # 경로 파라미터로 제조사 ID를 받음
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):
    """
    특정 제조사(Maker)의 상세 정보를 조회하는 API 엔드포인트입니다.

    Args:
        maker_id (str): 조회할 제조사 ID.
        db (Session): SQLAlchemy 데이터베이스 세션.

    Returns:
        dict: 조회된 제조사 상세 정보.

    Raises:
        HTTPException: 제조사 ID를 찾지 못한 경우 404 Not Found.
    """
    maker = crud.get_maker_by_id(db, maker_id)  # CRUD 함수를 통해 제조사 조회
    if not maker:
        raise HTTPException(status_code=404, detail="제조사를 찾을 수 없습니다.")

    # Maker 객체를 딕셔너리로 변환하여 반환
    return {
        "id": maker.id,
        "name": maker.name,
        "created_at": maker.created_at,
        "updated_at": maker.updated_at,
    }


@handler.put("/{maker_id}")
def update_maker(
    maker_id: str,  # 경로 파라미터로 제조사 ID를 받음
    maker_update: schemas.MakerUpdate,  # 요청 바디는 MakerUpdate 스키마를 따름
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):
    """
    특정 제조사(Maker)의 정보를 업데이트하는 API 엔드포인트입니다.

    Args:
        maker_id (str): 업데이트할 제조사 ID.
        maker_update (schemas.MakerUpdate): 업데이트할 제조사 정보를 담은 DTO.
        db (Session): SQLAlchemy 데이터베이스 세션.

    Returns:
        dict: 업데이트된 제조사 정보와 성공 메시지.

    Raises:
        HTTPException: 제조사 ID를 찾지 못한 경우 404 Not Found.
    """
    updated_maker = crud.update_maker(
        db, maker_id, maker_update.name
    )  # CRUD 함수를 통해 제조사 업데이트
    if not updated_maker:
        raise HTTPException(status_code=404, detail="제조사를 찾을 수 없습니다.")

    # 업데이트된 제조사 정보를 포함하는 응답 반환
    return {
        "id": updated_maker.id,
        "name": updated_maker.name,
        "updated_at": updated_maker.updated_at,
        "message": "제조사 정보가 성공적으로 업데이트되었습니다.",
    }


@handler.delete("/{maker_id}")
def delete_maker(
    maker_id: str,  # 경로 파라미터로 제조사 ID를 받음
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):
    """
    특정 제조사(Maker)를 삭제하는 API 엔드포인트입니다.
    - 해당 제조사에 연결된 부품(Resources)이 있는 경우 외래 키 제약 조건으로 인해 삭제가 실패할 수 있습니다.

    Args:
        maker_id (str): 삭제할 제조사 ID.
        db (Session): SQLAlchemy 데이터베이스 세션.

    Returns:
        dict: 삭제 성공 메시지와 삭제된 제조사 ID.

    Raises:
        HTTPException: 제조사 ID를 찾지 못한 경우 404 Not Found.
    """
    success = crud.delete_maker(db, maker_id)  # CRUD 함수를 통해 제조사 삭제
    if not success:
        raise HTTPException(status_code=404, detail="제조사를 찾을 수 없습니다.")

    # 삭제 성공 메시지 반환
    return {"message": "제조사가 성공적으로 삭제되었습니다.", "deleted_id": maker_id}
