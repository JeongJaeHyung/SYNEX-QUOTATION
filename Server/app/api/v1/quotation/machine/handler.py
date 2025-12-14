# api/v1/quotation/machine/handler.py
#
# 장비 견적서(Machine) 관련 API 엔드포인트를 정의합니다.
# - 견적서 생성, 목록 조회, 검색, 상세 조회, 수정 기능을 제공합니다.
# - 견적서에 포함되는 자재(Resources)의 검증 및 상세 정보 처리를 포함합니다.
#

from fastapi import APIRouter, Depends, HTTPException, Query # FastAPI 라우터, 의존성 주입, HTTP 예외 처리, 쿼리 파라미터
from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위함
from typing import Optional, Union # 타입 힌트 (선택적 인자, Union 타입)
from uuid import UUID # UUID 타입 (경로 파라미터 등)
from database import get_db # 데이터베이스 세션 의존성 주입
from api.v1.quotation.machine import schemas, crud # Machine 스키마(DTO) 및 CRUD 함수 임포트
from models.resources import Resources # Resources 모델 임포트 (자재 존재 여부 검증용)

# API 라우터 인스턴스 생성
handler = APIRouter()

# ============================================================
# 스키마 생성 헬퍼 함수
# ============================================================

def get_machine_list_schema() -> dict:
    """
    견적서 목록 조회 응답 DTO의 스키마 정의를 반환합니다.
    - 프론트엔드에서 테이블 헤더 및 컬럼 속성을 동적으로 생성할 때 사용될 수 있습니다.
    
    Returns:
        dict: MachineList 스키마 정의 딕셔너리.
    """
    return {
        "name": {
            "title": "장비명",
            "type": "string",
            "ratio": 4,
            "align": "left"
        },
        "manufacturer": {
            "title": "장비사", # 또는 "Maker" - 원하는 대로 선택
            "type": "string",
            "ratio": 2,
            "align": "center"
        },
        "client": {
            "title": "고객사",
            "type": "string",
            "ratio": 2,
            "align": "center"
        },
        "creator": {
            "title": "작성자",
            "type": "string",
            "ratio": 1,
            "align": "center"
        },
        "updated_at": {
            "title": "최종수정일",
            "type": "datetime",
            "format": "YYYY-MM-DD HH:mm",
            "ratio": 2,
            "align": "center"
        },
        "description": {
            "title": "비고",
            "type": "string",
            "ratio": 3,
            "align": "left"
        }
    }

def get_machine_resources_schema() -> dict:
    """
    견적서 구성 자재(MachineResources) 상세 조회 응답 DTO의 스키마 정의를 반환합니다.
    - 프론트엔드에서 견적서 상세 화면의 자재 테이블 헤더를 구성할 때 사용될 때 사용될 수 있습니다.
    
    Returns:
        dict: MachineResources 스키마 정의 딕셔너리.
    """
    return {
        "item_code": {
            "title": "품목코드",
            "type": "string",
            "ratio": 2
        },
        "maker_name": {
            "title": "Maker",
            "type": "string",
            "ratio": 2
        },
        "category_major": {
            "title": "Unit",
            "type": "string",
            "ratio": 2
        },
        "category_minor": {
            "title": "품목",
            "type": "string",
            "ratio": 2
        },
        "model_name": {
            "title": "모델명/규격",
            "type": "string",
            "ratio": 3
        },
        "unit": {
            "title": "단위",
            "type": "string",
            "ratio": 1
        },
        "solo_price": {
            "title": "금액",
            "type": "integer",
            "format": "currency",
            "ratio": 2
        },
        "quantity": {
            "title": "수량",
            "type": "integer",
            "ratio": 1
        },
        "subtotal": {
            "title": "합계 금액",
            "type": "integer",
            "format": "currency",
            "ratio": 2
        }
    }

# ============================================================
# Machine Endpoints (견적서 관련 API)
# ============================================================

@handler.post("/", response_model=schemas.MachineCreateResponse, status_code=201)
def register_machine(
    machine: schemas.MachineCreate, # 요청 바디는 MachineCreate 스키마를 따름
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    """
    새로운 장비 견적서(Machine)를 등록하는 API 엔드포인트입니다.
    - 견적서에 포함된 실제 부품(Resources)들의 존재 여부를 검증합니다.
    - 견적서와 관련된 자재 정보(MachineResources)를 함께 저장합니다.
    
    Args:
        machine (schemas.MachineCreate): 등록할 견적서 및 자재 정보를 담은 DTO.
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        schemas.MachineCreateResponse: 생성된 견적서 상세 정보를 담은 DTO.
        
    Raises:
        HTTPException: 견적서에 포함된 자재 중 마스터에 없는 것이 있을 경우 404 Not Found.
    """
    # ========== 실제 부품 존재 여부 검증 ==========
    # 견적서에 포함된 자재 목록을 순회하며, 각 자재가 Resources 마스터에 실제로 등록되어 있는지 확인합니다.
    for resource in machine.resources:
        # SUMMARY (집계 항목) 또는 LABOR (인건비 항목)은 마스터에 직접 등록된 자재가 아니므로 검증을 스킵합니다.
        if resource.maker_id in ["SUMMARY", "LABOR", "T000"]: # 'T000'도 특수 목적으로 사용될 수 있으므로 포함
            continue
        
        # Resources 테이블에서 해당 maker_id와 resources_id를 가진 실제 부품이 있는지 조회합니다.
        existing_resource = db.query(Resources).filter(
            Resources.maker_id == resource.maker_id,
            Resources.id == resource.resources_id
        ).first()
        
        if not existing_resource:
            # 마스터에 없는 부품이 포함된 경우 에러를 발생시킵니다.
            raise HTTPException(
                status_code=404,
                detail=f"자재를 찾을 수 없습니다: {resource.maker_id}-{resource.resources_id}"
            )
    
    # ========== Machine 생성 ==========
    # Pydantic 모델의 리소스 목록을 딕셔너리 리스트로 변환하여 CRUD 함수에 전달합니다.
    resources_data = [r.dict() for r in machine.resources]
    db_machine = crud.create_machine(
        db=db,
        name=machine.name,
        manufacturer=machine.manufacturer,
        client=machine.client,
        creator=machine.creator,
        description=machine.description,
        resources=resources_data # 자재 데이터와 함께 Machine 생성
    )
    
    # ========== Resources 상세 정보 조회 및 총액 계산 ==========
    # 생성된 Machine의 ID를 사용하여 자재 상세 정보(MachineResources, Resources 조인)를 다시 조회합니다.
    # 이 과정에서 SUMMARY/LABOR 항목은 가상 데이터로 처리됩니다.
    resources_detail = crud.get_machine_resources_detail(db, db_machine.id)
    
    # 조회된 자재 상세 정보에서 각 자재의 소계(subtotal)를 합산하여 최종 총액을 계산합니다.
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    # 생성된 견적서의 상세 정보를 포함하는 응답을 반환합니다.
    return {
        "id": db_machine.id,
        "name": db_machine.name,
        "manufacturer": db_machine.manufacturer,
        "client": db_machine.client,
        "creator": db_machine.creator,
        "description": db_machine.description,
        "created_at": db_machine.created_at,
        "total_price": total_price,
        "resource_count": len(resources_detail),
        "resources": { "items": resources_detail } # resources 필드를 DTO 규격에 맞춰 items로 감쌈
    }


@handler.get("/", response_model=Union[schemas.MachineListWithSchemaResponse, schemas.MachineListResponse])
def get_machines(
    include_schema: bool = Query(False, description="응답에 스키마 정의를 포함할지 여부"),
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=100, description="가져올 최대 레코드 수"),
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    """
    모든 장비 견적서(Machine) 목록을 조회하는 API 엔드포인트입니다.
    - 최신 수정일 기준으로 정렬되며, 페이징 및 스키마 포함 옵션을 지원합니다.
    
    Args:
        include_schema (bool): 응답에 스키마 정의를 포함할지 여부.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        Union[schemas.MachineListWithSchemaResponse, schemas.MachineListResponse]:
            견적서 목록과 페이징 정보를 담은 응답 DTO.
    """
    total, machines = crud.get_machines(db, skip=skip, limit=limit)
    
    # Machine 객체 리스트를 DTO 형식의 딕셔너리 리스트로 변환합니다.
    items = [
        {
            "id": m.id,
            "name": m.name,
            "manufacturer": m.manufacturer,
            "client": m.client,
            "creator": m.creator,
            "description": m.description,
            "updated_at": m.updated_at
        }
        for m in machines
    ]
    
    # 스키마 포함 옵션에 따라 응답을 구성합니다.
    if include_schema:
        return {
            "schema": get_machine_list_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }
    else:
        return {
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }


@handler.get("/search", response_model=Union[schemas.MachineListWithSchemaResponse, schemas.MachineListResponse])
def search_machines(
    search: str = Query(..., min_length=1, description="검색어"),
    include_schema: bool = Query(False, description="응답에 스키마 정의를 포함할지 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    """
    검색어를 사용하여 장비 견적서(Machine) 목록을 조회하는 API 엔드포인트입니다.
    - 견적서 이름에 대한 부분 매칭을 수행합니다.
    - 페이징 및 스키마 포함 옵션을 지원합니다.
    
    Args:
        search (str): 견적서 이름에서 검색할 문자열 (최소 1자).
        include_schema (bool): 응답에 스키마 정의를 포함할지 여부.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        Union[schemas.MachineListWithSchemaResponse, schemas.MachineListResponse]:
            검색된 견적서 목록과 페이징 정보를 담은 응답 DTO.
    """
    total, machines = crud.search_machines(db, search=search, skip=skip, limit=limit)
    
    # Machine 객체 리스트를 DTO 형식의 딕셔너리 리스트로 변환합니다.
    items = [
        {
            "id": m.id,
            "name": m.name,
            "manufacturer": m.manufacturer,
            "client": m.client,
            "creator": m.creator,
            "description": m.description,
            "updated_at": m.updated_at
        }
        for m in machines
    ]
    
    # 스키마 포함 옵션에 따라 응답을 구성합니다.
    if include_schema:
        return {
            "schema": get_machine_list_schema(),
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }
    else:
        return {
            "total": total,
            "items": items,
            "skip": skip,
            "limit": limit
        }


@handler.get("/{machine_id}", response_model=schemas.MachineDetailResponse)
def get_machine(
    machine_id: UUID, # 경로 파라미터로 견적서 ID를 받음
    include_schema: bool = Query(False, description="응답에 스키마 정의를 포함할지 여부"),
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    """
    특정 장비 견적서(Machine)의 상세 정보를 조회하는 API 엔드포인트입니다.
    - 견적서의 기본 정보와 구성 자재(MachineResources) 상세 정보를 함께 반환합니다.
    
    Args:
        machine_id (UUID): 조회할 견적서 ID.
        include_schema (bool): 응답에 스키마 정의를 포함할지 여부.
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        schemas.MachineDetailResponse: 조회된 견적서 상세 정보 및 자재 목록을 담은 DTO.
        
    Raises:
        HTTPException: 견적서를 찾을 수 없는 경우 404 Not Found.
    """
    machine = crud.get_machine_by_id(db, machine_id) # CRUD 함수를 통해 Machine 조회 (MachineResources 함께 로드)
    if not machine:
        raise HTTPException(status_code=404, detail="견적서를 찾을 수 없습니다.")
    
    # Resources 상세 정보 (SUMMARY/LABOR 항목 포함하여 가공된 데이터)를 조회합니다.
    resources_detail = crud.get_machine_resources_detail(db, machine_id)
    # 조회된 자재 상세 정보에서 각 자재의 소계(subtotal)를 합산하여 최종 총액을 계산합니다.
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    # 스키마 포함 옵션에 따라 응답을 구성합니다.
    if include_schema:
        return {
            "id": machine.id,
            "name": machine.name,
            "manufacturer": machine.manufacturer,
            "client": machine.client,
            "creator": machine.creator,
            "price": machine.price,
            "description": machine.description,
            "created_at": machine.created_at,
            "updated_at": machine.updated_at,
            "total_price": total_price, # 계산된 총액 추가
            "resource_count": len(resources_detail), # 자재 개수 추가
            "resources": { # resources 필드를 DTO 규격에 맞춰 schema와 items로 감쌈
                "schema": get_machine_resources_schema(),
                "items": resources_detail
            }
        }
    
    # 스키마를 포함하지 않는 경우의 응답
    return {
        "id": machine.id,
        "name": machine.name,
        "manufacturer": machine.manufacturer,
        "client": machine.client,
        "creator": machine.creator,
        "price": machine.price,
        "description": machine.description,
        "created_at": machine.created_at,
        "updated_at": machine.updated_at,
        "total_price": total_price, # 계산된 총액 추가
        "resource_count": len(resources_detail), # 자재 개수 추가
        "resources": resources_detail # 스키마 없이 자재 리스트만 반환
    }


@handler.put("/{machine_id}", response_model=schemas.MachineUpdateResponse)
def update_machine(
    machine_id: UUID, # 경로 파라미터로 견적서 ID를 받음
    machine_update: schemas.MachineUpdate, # 요청 바디는 MachineUpdate 스키마를 따름
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    """
    특정 장비 견적서(Machine)의 정보를 업데이트하는 API 엔드포인트입니다.
    - 견적서의 기본 정보와 구성 자재(MachineResources)를 업데이트합니다.
    - 구성 자재는 기존 것을 모두 삭제하고 새로 받은 자재 목록으로 대체합니다.
    
    Args:
        machine_id (UUID): 업데이트할 견적서 ID.
        machine_update (schemas.MachineUpdate): 업데이트할 견적서 정보를 담은 DTO.
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        schemas.MachineUpdateResponse: 업데이트된 견적서 상세 정보를 담은 DTO.
        
    Raises:
        HTTPException: 견적서를 찾을 수 없거나 자재 중 마스터에 없는 것이 있을 경우 404 Not Found.
    """
    # ========== 실제 부품 존재 여부 검증 ==========
    # 업데이트 요청에 자재 목록이 포함된 경우, 각 자재가 Resources 마스터에 실제로 등록되어 있는지 확인합니다.
    if machine_update.resources:
        for resource in machine_update.resources:
            # SUMMARY 또는 LABOR 항목은 마스터에 직접 등록된 자재가 아니므로 검증을 스킵합니다.
            if resource.maker_id in ["SUMMARY", "LABOR", "T000"]:
                continue
            
            # Resources 테이블에서 해당 maker_id와 resources_id를 가진 실제 부품이 있는지 조회합니다.
            existing_resource = db.query(Resources).filter(
                Resources.maker_id == resource.maker_id,
                Resources.id == resource.resources_id
            ).first()
            
            if not existing_resource:
                # 마스터에 없는 부품이 포함된 경우 에러를 발생시킵니다.
                raise HTTPException(
                    status_code=404,
                    detail=f"자재를 찾을 수 없습니다: {resource.maker_id}-{resource.resources_id}"
                )
    
    # ========== Resources 데이터 변환 ==========
    # Pydantic 모델의 리소스 목록을 딕셔너리 리스트로 변환하여 CRUD 함수에 전달합니다.
    resources_data = None
    if machine_update.resources: # resources 필드가 제공되었을 경우에만 변환
        resources_data = [r.dict() for r in machine_update.resources]
    
    # ========== 견적서 업데이트 (CRUD 호출) ==========
    updated_machine = crud.update_machine(
        db=db,
        machine_id=machine_id,
        name=machine_update.name,
        manufacturer=machine_update.manufacturer,
        client=machine_update.client,
        description=machine_update.description,
        resources=resources_data # 자재 데이터와 함께 Machine 업데이트
    )
    
    if not updated_machine:
        raise HTTPException(status_code=404, detail="견적서를 찾을 수 없습니다.")
    
    # ========== 업데이트된 Resources 상세 정보 조회 및 총액 계산 ==========
    # 업데이트된 Machine의 ID를 사용하여 자재 상세 정보(MachineResources, Resources 조인)를 다시 조회합니다.
    resources_detail = crud.get_machine_resources_detail(db, machine_id)
    # 조회된 자재 상세 정보에서 각 자재의 소계(subtotal)를 합산하여 최종 총액을 계산합니다.
    total_price = sum(r['subtotal'] for r in resources_detail)
    
    # 업데이트된 견적서의 상세 정보를 포함하는 응답을 반환합니다.
    return {
        "id": updated_machine.id,
        "name": updated_machine.name,
        "manufacturer": updated_machine.manufacturer,
        "client": updated_machine.client,
        "creator": updated_machine.creator,
        "description": updated_machine.description,
        "updated_at": updated_machine.updated_at,
        "total_price": total_price, # 계산된 총액 추가
        "resource_count": len(resources_detail), # 자재 개수 추가
        "resources": resources_detail # 스키마 없이 자재 리스트만 반환
    }