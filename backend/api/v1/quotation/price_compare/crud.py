# SYNEX+QUOTATION/backend/api/v1/quotation/price_compare/crud.py

from typing import Dict, List, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from backend.models.machine import Machine
from backend.models.machine_resources import MachineResources

# Models Import
from backend.models.price_compare import PriceCompare
from backend.models.price_compare_machine import PriceCompareMachine
from backend.models.price_compare_resources import PriceCompareResources

from . import schemas


# ============================================================
# Helper Logic: 초기 리소스 자동 계산 (BOM Aggregation)
# ============================================================
def calculate_initial_resources(db: Session, machine_ids: list[UUID]) -> list[dict]:
    """
    선택된 장비들의 BOM을 집계하고 출장경비 및 관리비를 추가합니다.
    - 인건비: major는 유지하고, minor(구분)는 model_name을 가져옵니다.
    - 자재비: major는 "자재비"로 고정하고, minor(구분)는 원본 대분류를 가져와 집계합니다.
    - 견적 단가(quotation_solo_price): 내정가 합계에서 15% 증가된 금액으로 초기화합니다. 💡
    """

    # 1. 리소스 + 장비명 조회
    results = (
        db.query(MachineResources, Machine.name)
        .join(Machine, MachineResources.machine_id == Machine.id)
        .filter(MachineResources.machine_id.in_(machine_ids))
        .all()
    )

    # 2. 메모리 상에서 집계
    aggregated: dict[tuple, dict] = {}

    for res, machine_name in results:
        is_labor = (res.maker_id == "LABOR") or (
            res.display_major and "인건비" in res.display_major
        )

        if is_labor:
            major = res.display_major if res.display_major else "인건비"
            minor = res.display_model_name if res.display_model_name else "인건비 상세"
        else:
            major = "자재비"
            minor = res.display_major if res.display_major else "기타 자재"

        key = (res.machine_id, machine_name, major, minor)

        if key not in aggregated:
            aggregated[key] = {
                "price": 0,
                "display_unit": res.display_unit
                if res.display_unit
                else ("M/D" if is_labor else "ea"),
            }

        # 합계 금액 계산 (내정가 기준)
        aggregated[key]["price"] += res.solo_price * res.quantity

    # 3. 결과 리스트 변환 (15% 할증 로직 적용) 💡
    initial_data = []
    for (m_id, m_name, major, minor), data in aggregated.items():
        base_price = data["price"]
        # 💡 요구사항 반영: 견적 단가를 내정가보다 15% 증가된 금액으로 저장
        increased_price = int(base_price * 1.15)

        initial_data.append(
            {
                "machine_id": m_id,
                "machine_name": m_name,
                "major": major,
                "minor": minor,
                "cost_solo_price": base_price,
                "cost_unit": data["display_unit"],
                "cost_compare": 1,
                "quotation_solo_price": increased_price,  # 💡 15% 증가 반영
                "quotation_unit": data["display_unit"],
                "quotation_compare": 1,
                "upper": 15.0,
                "description": None,
            }
        )

    # 4. 가상 항목 추가 (출장경비 & 관리비)
    first_machine_id = machine_ids[0] if machine_ids else None

    # 4-1. 출장경비 리스트
    business_trip_items = {"교통비": "MD", "식대": "MD", "운송비": "원", "숙박비": "MD"}
    for item, unit in business_trip_items.items():
        initial_data.append(
            {
                "machine_id": first_machine_id,
                "machine_name": item,
                "major": "출장경비",
                "minor": item,
                "cost_solo_price": 0,
                "cost_unit": unit,
                "cost_compare": 1,
                "quotation_solo_price": 0,
                "quotation_unit": unit,
                "quotation_compare": 1,
                "upper": 15.0,
                "description": "",
            }
        )

    # 4-2. 관리비 리스트 (자재비 + 인건비 + 출장경비 합계 기준 계산)
    # 자재비, 인건비, 출장경비 합계 계산
    base_total = 0
    for item in initial_data:
        if item["major"] in ["자재비", "인건비", "출장경비"]:
            base_total += item["quotation_solo_price"] * item["quotation_compare"]

    # 관리비 비율 설정 (일반관리비: 3%, 기업이윤: 10%)
    overhead_rates = {
        "일반관리비": 0.03,  # 3%
        "기업이윤": 0.10,  # 10%
    }

    for item, rate in overhead_rates.items():
        calculated_price = int(base_total * rate)
        initial_data.append(
            {
                "machine_id": first_machine_id,
                "machine_name": item,
                "major": "관리비",
                "minor": item,
                "cost_solo_price": calculated_price,
                "cost_unit": "%",
                "cost_compare": 1,
                "quotation_solo_price": calculated_price,
                "quotation_unit": "%",
                "quotation_compare": 1,
                "upper": 0.0,  # 관리비는 비율 계산이므로 상승률 0
                "description": f"{int(rate * 100)}% 적용",
            }
        )

    return initial_data


# ============================================================
# CRUD Functions
# ============================================================


def create_price_compare(
    db: Session, request: schemas.PriceCompareCreate
) -> PriceCompare:
    # 폴더당 최대 1개의 PriceCompare만 허용
    existing = (
        db.query(PriceCompare)
        .filter(PriceCompare.folder_id == request.folder_id)
        .first()
    )
    if existing:
        raise ValueError(
            "이 폴더에는 이미 내정가 비교서가 존재합니다. 폴더당 최대 1개만 생성할 수 있습니다."
        )

    new_pc = PriceCompare(
        folder_id=request.folder_id,
        title=request.title,
        creator=request.creator,
        description=request.description,
    )
    db.add(new_pc)
    db.flush()

    for m_id in request.machine_ids:
        db.add(PriceCompareMachine(price_compare_id=new_pc.id, machine_id=m_id))

    calculated_items = calculate_initial_resources(db, request.machine_ids)
    for item in calculated_items:
        db.add(PriceCompareResources(price_compare_id=new_pc.id, **item))

    db.commit()
    db.refresh(new_pc)
    return new_pc


def get_price_compare(db: Session, pc_id: UUID) -> PriceCompare:
    return db.query(PriceCompare).filter(PriceCompare.id == pc_id).first()


def update_price_compare_overwrite(
    db: Session, pc_id: UUID, request: schemas.PriceCompareUpdate
) -> PriceCompare:
    pc = get_price_compare(db, pc_id)
    if not pc:
        return None

    if request.title is not None:
        pc.title = request.title
    if request.creator is not None:
        pc.creator = request.creator
    if request.description is not None:
        pc.description = request.description

    db.query(PriceCompareMachine).filter(
        PriceCompareMachine.price_compare_id == pc_id
    ).delete()
    for m_id in request.machine_ids:
        db.add(PriceCompareMachine(price_compare_id=pc_id, machine_id=m_id))

    db.query(PriceCompareResources).filter(
        PriceCompareResources.price_compare_id == pc_id
    ).delete()

    if request.price_compare_resources is not None:
        target_data = [res.model_dump() for res in request.price_compare_resources]
    else:
        target_data = calculate_initial_resources(db, request.machine_ids)

    for item in target_data:
        db.add(PriceCompareResources(price_compare_id=pc_id, **item))

    db.commit()
    db.refresh(pc)
    return pc


# ============================================================
# Delete (삭제)
# ============================================================
def delete_price_compare(db: Session, price_compare_id: UUID) -> bool:
    """
    내정가 비교서 삭제
    - 관련 PriceCompareMachine, PriceCompareResources도 cascade로 삭제됩니다.
    """
    pc = get_price_compare(db, price_compare_id)
    if not pc:
        return False

    db.delete(pc)
    db.commit()
    return True
