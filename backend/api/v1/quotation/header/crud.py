# backend/api/v1/quotation/header/crud.py
from collections import defaultdict
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.detailed import Detailed
from backend.models.detailed_resources import DetailedResources

# Models Import
from backend.models.header import Header
from backend.models.header_resources import HeaderResources
from backend.models.price_compare_resources import PriceCompareResources

# ============================================================
# CRUD Functions
# ============================================================


def create_header(
    db: Session,
    folder_id: UUID,
    detailed_id: UUID,
    title: str,
    quotation_number: str | None,
    creator: str,
    client: str,
    manufacturer: str | None,
    pic_name: str,
    pic_position: str,
) -> Header:
    """
    Header 생성 + HeaderResources 자동 생성

    처리 로직:
    1. DetailedResources에서 major가 "자재비", "인건비"인 항목들을 machine별로 그룹화
    2. 각 machine별로 "재료비", "인건비" 2개 항목 생성
    3. major가 "출장 경비"인 모든 항목을 합산 → machine="경비", name="경비" 1개 생성
    4. PriceCompareResources의 major="관리비" 항목들 합산 → machine="안전관리비 및 기업이윤" 1개 생성
    """
    # 폴더당 최대 1개의 Header만 허용
    existing = db.query(Header).filter(Header.folder_id == folder_id).first()
    if existing:
        raise ValueError(
            "이 폴더에는 이미 갑지가 존재합니다. 폴더당 최대 1개만 생성할 수 있습니다."
        )

    # 1. Detailed 조회
    detailed = db.query(Detailed).filter(Detailed.id == detailed_id).first()
    if not detailed:
        raise ValueError("Detailed not found")

    price_compare_id = detailed.price_compare_id

    # 2. DetailedResources 조회
    detailed_resources = (
        db.query(DetailedResources)
        .filter(DetailedResources.detailed_id == detailed_id)
        .all()
    )

    # 3. 데이터 그룹화
    machine_groups = defaultdict(
        lambda: {"자재비": 0, "인건비": 0}
    )  # machine별 자재비/인건비
    travel_expense_total = 0  # 출장 경비 전체 합계
    machines = set()

    for resource in detailed_resources:
        major_normalized = resource.major.replace(" ", "")

        if major_normalized == "자재비":
            machines.add(resource.machine_name)
            machine_groups[resource.machine_name]["자재비"] += (
                resource.solo_price * resource.compare
            )

        elif major_normalized == "인건비":
            machines.add(resource.machine_name)
            machine_groups[resource.machine_name]["인건비"] += (
                resource.solo_price * resource.compare
            )

        elif major_normalized == "출장경비":
            # 모든 "출장 경비" 항목 합산
            travel_expense_total += resource.solo_price * resource.compare

    # 4. Header 생성
    header = Header(
        folder_id=folder_id,
        title=title,
        quotation_number=quotation_number,
        creator=creator,
        client=client,
        manufacturer=manufacturer,
        pic_name=pic_name,
        pic_position=pic_position,
        price=0,
    )
    db.add(header)
    db.flush()

    # 5. HeaderResources 생성
    header_resources_list = []

    # 각 machine별로 재료비/인건비 생성
    for machine in sorted(machines):
        # 재료비 ("자재비" → "재료비")
        header_resources_list.append(
            HeaderResources(
                header_id=header.id,
                machine=machine,
                name="재료비",
                solo_price=machine_groups[machine]["자재비"],
                compare=1,
                unit="원",
                spac="",
                description="",
            )
        )

        # 인건비
        header_resources_list.append(
            HeaderResources(
                header_id=header.id,
                machine=machine,
                name="인건비",
                solo_price=machine_groups[machine]["인건비"],
                compare=1,
                unit="원",
                spac="",
                description="",
            )
        )

    # 6. PriceCompareResources에서 관리비 합산 (단가 * 수량)
    price_compare_resources = (
        db.query(PriceCompareResources)
        .filter(
            PriceCompareResources.price_compare_id == price_compare_id,
            PriceCompareResources.major == "관리비",
        )
        .all()
    )

    total_admin_cost = sum(
        resource.quotation_solo_price * resource.quotation_compare
        for resource in price_compare_resources
    )

    # 경비 (출장 경비 전체 합산) - 하단으로 이동
    header_resources_list.append(
        HeaderResources(
            header_id=header.id,
            machine=" ",  # 공백으로 설정
            name="경비",
            solo_price=travel_expense_total,
            compare=1,
            unit="원",
            spac="",
            description="",
        )
    )

    # 안전관리비 및 기업이윤 - 최하단
    header_resources_list.append(
        HeaderResources(
            header_id=header.id,
            machine=" ",  # 공백으로 설정
            name="안전관리비 및 기업이윤",
            solo_price=int(total_admin_cost),
            compare=1,
            unit="원",
            spac="",
            description="",
        )
    )

    # 7. HeaderResources 저장
    for hr in header_resources_list:
        db.add(hr)

    # 8. 최종 price 계산
    total_price = sum(hr.solo_price * hr.compare for hr in header_resources_list)
    header.price = total_price

    db.commit()
    db.refresh(header)
    return header


def get_header_by_id(db: Session, header_id: UUID) -> Header | None:
    """Header 단일 조회"""
    return db.query(Header).filter(Header.id == header_id).first()


def get_header_resources(db: Session, header_id: UUID) -> list[dict]:
    """
    HeaderResources 조회 (subtotal 포함)

    반환: machine, name, spac, compare, unit, solo_price, subtotal, description
    """
    resources = (
        db.query(HeaderResources).filter(HeaderResources.header_id == header_id).all()
    )
    result = []
    for r in resources:
        result.append(
            {
                "machine": r.machine,
                "name": r.name,
                "spac": r.spac,
                "compare": r.compare,
                "unit": r.unit,
                "solo_price": r.solo_price,
                "subtotal": r.solo_price * r.compare,
                "description": r.description,
            }
        )
    return result


def update_header(
    db: Session,
    header_id: UUID,
    title: str | None = None,
    quotation_number: str | None = None,
    creator: str | None = None,
    client: str | None = None,
    manufacturer: str | None = None,
    pic_name: str | None = None,
    pic_position: str | None = None,
    description_1: str | None = None,
    description_2: str | None = None,
    best_nego_total: int | None = None,
    price: int | None = None,
    header_resources: list[dict] | None = None,
) -> Header | None:
    """
    Header 수정 (부분 수정)

    - 기본 정보 수정
    - header_resources 전체 교체 (선택)
    - price: 클라이언트에서 직접 지정하거나, header_resources 제공 시 자동 계산
    """
    header = get_header_by_id(db, header_id)
    if not header:
        return None

    # 기본 정보 수정
    if title is not None:
        header.title = title
    if quotation_number is not None:
        header.quotation_number = quotation_number
    if creator is not None:
        header.creator = creator
    if client is not None:
        header.client = client
    if manufacturer is not None:
        header.manufacturer = manufacturer
    if pic_name is not None:
        header.pic_name = pic_name
    if pic_position is not None:
        header.pic_position = pic_position
    if description_1 is not None:
        header.description_1 = description_1
    if description_2 is not None:
        header.description_2 = description_2
    if best_nego_total is not None:
        header.best_nego_total = best_nego_total

    # HeaderResources 수정 (제공된 경우)
    if header_resources is not None:
        # 기존 resources 삭제
        db.query(HeaderResources).filter(
            HeaderResources.header_id == header_id
        ).delete()
        db.flush()

        # 새 resources 추가
        for resource in header_resources:
            hr = HeaderResources(
                header_id=header_id,
                machine=resource["machine"],
                name=resource["name"],
                spac=resource.get("spac", ""),
                compare=resource["compare"],
                unit=resource["unit"],
                solo_price=resource["solo_price"],
                description=resource.get("description", ""),
            )
            db.add(hr)

        # price: 클라이언트에서 명시적으로 지정하지 않으면 자동 계산
        if price is None:
            header.price = sum(r["solo_price"] * r["compare"] for r in header_resources)
        else:
            header.price = price
    elif price is not None:
        # header_resources 없이 price만 수정
        header.price = price

    db.commit()
    db.refresh(header)
    return header


def delete_header(db: Session, header_id: UUID) -> bool:
    """Header 삭제 (CASCADE로 HeaderResources도 자동 삭제)"""
    header = get_header_by_id(db, header_id)
    if not header:
        return False
    db.delete(header)
    db.commit()
    return True
