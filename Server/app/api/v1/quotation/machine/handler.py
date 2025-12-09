# SYNEX+QUOTATION/Server/app/api/v1/quotation/machine/handler.py
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from database import get_db
from . import crud, schemas

handler = APIRouter()


@handler.post(
    "",
    response_model=schemas.MachineResponse,
    status_code=201,
    summary="Machine 등록",
    description="새로운 기계와 구성 부품을 등록합니다. quantity가 0인 부품은 자동으로 제외됩니다."
)
async def create_machine(
    machine_data: schemas.MachineCreate,
    db: Session = Depends(get_db)
):
    """
    Machine 등록
    
    - **name**: 기계명 (최대 100자)
    - **resources**: 구성 부품 목록
      - quantity >= 1인 부품만 등록됨
      - quantity = 0인 부품은 자동 제외
    """
    # 모든 부품이 존재하는지 확인
    for resource in machine_data.resources:
        if not crud.check_resources_exist(db, resource.maker_id, resource.resources_id):
            raise HTTPException(
                status_code=404,
                detail=f"Resource not found: {resource.resources_id} (Maker: {resource.maker_id})"
            )
    
    # Machine 생성
    resources_data = [resource.model_dump() for resource in machine_data.resources]
    machine = crud.create_machine(
        db=db,
        name=machine_data.name,
        resources_data=resources_data
    )
    
    # 상세 조회하여 응답
    machine = crud.get_machine_by_id(db, machine.id)
    
    # 응답 형식으로 변환
    formatted_resources = [
        crud.format_machine_resource_response(mr)
        for mr in machine.machine_resources
    ]
    
    total_price = crud.calculate_total_price(machine.machine_resources)
    
    return {
        "id": machine.id,
        "name": machine.name,
        "created_at": machine.created_at,
        "updated_at": machine.updated_at,
        "total_price": total_price,
        "resource_count": len(formatted_resources),
        "resources": formatted_resources
    }


@handler.get(
    "",
    response_model=schemas.MachineListResponse,
    summary="Machine 목록 조회",
    description="전체 기계 목록을 조회합니다. 최근 업데이트 순으로 정렬됩니다."
)
async def get_machine_list(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수 (최대 100)"),
    db: Session = Depends(get_db)
):
    """
    Machine 목록 조회
    
    - 최근 업데이트 순 정렬 (updated_at DESC)
    - 페이징 지원 (무한 스크롤 대응)
    """
    machines, total = crud.get_machine_list(db, skip=skip, limit=limit)
    
    items = [
        {
            "id": machine.id,
            "name": machine.name,
            "updated_at": machine.updated_at
        }
        for machine in machines
    ]
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }


@handler.get(
    "/search",
    response_model=schemas.MachineListResponse,
    summary="Machine 검색",
    description="기계명으로 검색합니다. 부분 매칭을 지원합니다."
)
async def search_machines(
    search: str = Query(..., min_length=1, description="검색어"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수 (최대 100)"),
    db: Session = Depends(get_db)
):
    """
    Machine 검색
    
    - 기계명 부분 매칭 (LIKE '%search%')
    - 최근 업데이트 순 정렬 (updated_at DESC)
    - 페이징 지원
    """
    machines, total = crud.search_machines(db, search_query=search, skip=skip, limit=limit)
    
    items = [
        {
            "id": machine.id,
            "name": machine.name,
            "updated_at": machine.updated_at
        }
        for machine in machines
    ]
    
    return {
        "total": total,
        "items": items,
        "skip": skip,
        "limit": limit
    }


@handler.get(
    "/{machine_id}",
    response_model=schemas.MachineResponse,
    summary="Machine 상세 조회",
    description="특정 기계의 상세 정보와 구성 부품 목록을 조회합니다."
)
async def get_machine_by_id(
    machine_id: UUID = Path(..., description="Machine UUID"),
    db: Session = Depends(get_db)
):
    """
    Machine 상세 조회
    
    - 기계 기본 정보
    - 구성 부품 전체 목록 (JOIN)
    - 부품별 상세 정보 (제조사, 카테고리, 인증 등)
    - 총 금액 계산
    """
    machine = crud.get_machine_by_id(db, machine_id)
    
    if not machine:
        raise HTTPException(status_code=404, detail=f"Machine not found: {machine_id}")
    
    # 응답 형식으로 변환
    formatted_resources = [
        crud.format_machine_resource_response(mr)
        for mr in machine.machine_resources
    ]
    
    total_price = crud.calculate_total_price(machine.machine_resources)
    
    return {
        "id": machine.id,
        "name": machine.name,
        "created_at": machine.created_at,
        "updated_at": machine.updated_at,
        "total_price": total_price,
        "resource_count": len(formatted_resources),
        "resources": formatted_resources
    }


@handler.put(
    "/{machine_id}",
    response_model=schemas.MachineResponse,
    summary="Machine 수정",
    description="기계 정보 및/또는 구성 부품을 수정합니다. 부품 목록은 전체 교체됩니다."
)
async def update_machine(
    machine_id: UUID = Path(..., description="Machine UUID"),
    machine_data: schemas.MachineUpdate = ...,
    db: Session = Depends(get_db)
):
    """
    Machine 수정
    
    - **name**: 기계명 수정 (Optional)
    - **resources**: 구성 부품 전체 교체 (Optional)
      - 기존 부품은 모두 삭제되고 새로 등록됨
      - quantity >= 1인 부품만 등록됨
    """
    # Machine 존재 확인
    existing_machine = crud.get_machine_by_id(db, machine_id)
    if not existing_machine:
        raise HTTPException(status_code=404, detail=f"Machine not found: {machine_id}")
    
    # 부품 존재 여부 확인
    if machine_data.resources:
        for resource in machine_data.resources:
            if not crud.check_resources_exist(db, resource.maker_id, resource.resources_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"Resource not found: {resource.resources_id} (Maker: {resource.maker_id})"
                )
    
    # Machine 수정
    resources_data = None
    if machine_data.resources:
        resources_data = [resource.model_dump() for resource in machine_data.resources]
    
    machine = crud.update_machine(
        db=db,
        machine_id=machine_id,
        name=machine_data.name,
        resources_data=resources_data
    )
    
    # 상세 조회하여 응답
    machine = crud.get_machine_by_id(db, machine.id)
    
    # 응답 형식으로 변환
    formatted_resources = [
        crud.format_machine_resource_response(mr)
        for mr in machine.machine_resources
    ]
    
    total_price = crud.calculate_total_price(machine.machine_resources)
    
    return {
        "id": machine.id,
        "name": machine.name,
        "created_at": machine.created_at,
        "updated_at": machine.updated_at,
        "total_price": total_price,
        "resource_count": len(formatted_resources),
        "resources": formatted_resources
    }