from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from backend.database import get_db
from . import schemas, crud

handler = APIRouter()

@handler.post(
    "", 
    response_model=schemas.PriceCompareResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="내정가 비교서 등록"
)
def create_price_compare(
    request: schemas.PriceCompareCreate, 
    db: Session = Depends(get_db)
):
    """
    **내정가 비교서 생성**
    - `machine_ids`의 장비 BOM을 집계하여 초기 데이터를 생성합니다.
    - 장비별로(`machine_id`) 부품을 나누고, 비고란에 `장비명`을 입력합니다.
    """
    new_pc = crud.create_price_compare(db, request)
    
    # Response Model의 machine_ids 필드를 채우기 위한 수동 매핑 💡
    # (ORM 관계 객체에서 ID 값만 뽑아내어 리스트로 만듦)
    new_pc.machine_ids = [pm.machine_id for pm in new_pc.price_compare_machines]
    
    return new_pc


@handler.get(
    "/{price_compare_id}", 
    response_model=schemas.PriceCompareResponse,
    summary="내정가 비교서 상세 조회"
)
def get_price_compare(
    price_compare_id: UUID, 
    db: Session = Depends(get_db)
):
    """
    **내정가 비교서 상세 조회**
    """
    pc = crud.get_price_compare(db, price_compare_id)
    if not pc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Price compare document not found"
        )
    
    # Response Model 매핑
    pc.machine_ids = [pm.machine_id for pm in pc.price_compare_machines]
    
    return pc


@handler.put(
    "/{price_compare_id}", 
    response_model=schemas.PriceCompareResponse,
    summary="내정가 비교서 수정 (전체 덮어쓰기)"
)
def update_price_compare(
    price_compare_id: UUID, 
    request: schemas.PriceCompareUpdate, 
    db: Session = Depends(get_db)
):
    """
    **내정가 비교서 수정**
    - `price_compare_resources` 리스트 **미전송(None)** 시: 
      변경된 장비 구성을 기준으로 BOM을 **자동 재계산(초기화)**합니다.
    - `price_compare_resources` 리스트 **전송** 시: 
      수동으로 입력된 값들을 **그대로 덮어쓰기(Overwrite)**합니다.
    """
    updated_pc = crud.update_price_compare_overwrite(db, price_compare_id, request)
    if not updated_pc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Price compare document not found"
        )
        
    # Response Model 매핑
    updated_pc.machine_ids = [pm.machine_id for pm in updated_pc.price_compare_machines]
    
    return updated_pc