# backend/api/v1/export/excel/crud.py
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any

from backend.models.header import Header
from backend.models.header_resources import HeaderResources
from backend.models.detailed import Detailed
from backend.models.detailed_resources import DetailedResources
from backend.models.price_compare import PriceCompare
from backend.models.price_compare_resources import PriceCompareResources


# ============================================================
# Header (갑지) 데이터 조회
# ============================================================
def get_header_data(db: Session, header_id: UUID) -> Dict[str, Any]:
    """
    Header 데이터 조회
    
    Returns:
        {
            "id": UUID,
            "title": str,
            "price": int,
            "creator": str,
            "client": str,
            "pic_name": str,
            "pic_position": str,
            "description_1": str,
            "description_2": str,
            "created_at": datetime,
            "updated_at": datetime,
            "resources": [
                {
                    "machine": str,
                    "name": str,
                    "spac": str,
                    "compare": int,
                    "unit": str,
                    "solo_price": int,
                    "subtotal": int,
                    "description": str
                }
            ]
        }
    """
    # Header 조회
    header = db.query(Header).filter(Header.id == header_id).first()
    if not header:
        raise ValueError(f"Header not found: {header_id}")
    
    # HeaderResources 조회
    resources = (
        db.query(HeaderResources)
        .filter(HeaderResources.header_id == header_id)
        .all()
    )
    
    # 데이터 변환
    resource_list = []
    for r in resources:
        resource_list.append({
            "machine": r.machine,
            "name": r.name,
            "spac": r.spac or "",
            "compare": r.compare,
            "unit": r.unit,
            "solo_price": r.solo_price,
            "subtotal": r.solo_price * r.compare,
            "description": r.description or ""
        })
    
    return {
        "id": str(header.id),
        "title": header.title,
        "price": header.price,
        "creator": header.creator,
        "client": header.client or "",
        "pic_name": header.pic_name or "",
        "pic_position": header.pic_position or "",
        "description_1": header.description_1 or "",
        "description_2": header.description_2 or "",
        "created_at": header.created_at,
        "updated_at": header.updated_at,
        "resources": resource_list
    }


# ============================================================
# Detailed (을지) 데이터 조회
# ============================================================
def get_detailed_data(db: Session, detailed_id: UUID) -> Dict[str, Any]:
    """
    Detailed 데이터 조회
    
    Returns:
        {
            "id": UUID,
            "creator": str,
            "description": str,
            "created_at": datetime,
            "updated_at": datetime,
            "resources": [
                {
                    "machine_name": str,
                    "major": str,
                    "minor": str,
                    "unit": str,
                    "solo_price": int,
                    "compare": int,
                    "subtotal": int,
                    "description": str
                }
            ]
        }
    """
    # Detailed 조회
    detailed = db.query(Detailed).filter(Detailed.id == detailed_id).first()
    if not detailed:
        raise ValueError(f"Detailed not found: {detailed_id}")
    
    # DetailedResources 조회
    resources = (
        db.query(DetailedResources)
        .filter(DetailedResources.detailed_id == detailed_id)
        .all()
    )
    
    # 데이터 변환
    resource_list = []
    for r in resources:
        resource_list.append({
            "machine_name": r.machine_name,
            "major": r.major,
            "minor": r.minor,
            "unit": r.unit,
            "solo_price": r.solo_price,
            "compare": r.compare,
            "subtotal": r.solo_price * r.compare,
            "description": r.description or ""
        })
    
    return {
        "id": str(detailed.id),
        "creator": detailed.creator,
        "description": detailed.description or "",
        "created_at": detailed.created_at,
        "updated_at": detailed.updated_at,
        "resources": resource_list
    }


# ============================================================
# PriceCompare (내정가견적비교서) 데이터 조회
# ============================================================
def get_price_compare_data(db: Session, price_compare_id: UUID) -> Dict[str, Any]:
    """
    PriceCompare 데이터 조회
    
    Returns:
        {
            "id": UUID,
            "creator": str,
            "description": str,
            "created_at": datetime,
            "updated_at": datetime,
            "resources": [
                {
                    "machine_id": UUID,
                    "machine_name": str,
                    "major": str,
                    "minor": str,
                    "cost_solo_price": int,
                    "cost_unit": str,
                    "cost_compare": int,
                    "quotation_solo_price": int,
                    "quotation_unit": str,
                    "quotation_compare": int,
                    "upper": float,
                    "description": str
                }
            ]
        }
    """
    # PriceCompare 조회
    price_compare = db.query(PriceCompare).filter(PriceCompare.id == price_compare_id).first()
    if not price_compare:
        raise ValueError(f"PriceCompare not found: {price_compare_id}")
    
    # PriceCompareResources 조회
    resources = (
        db.query(PriceCompareResources)
        .filter(PriceCompareResources.price_compare_id == price_compare_id)
        .all()
    )
    
    # 데이터 변환
    resource_list = []
    for r in resources:
        resource_list.append({
            "machine_id": str(r.machine_id),
            "machine_name": r.machine_name,
            "major": r.major,
            "minor": r.minor,
            "cost_solo_price": r.cost_solo_price,
            "cost_unit": r.cost_unit,
            "cost_compare": r.cost_compare,
            "quotation_solo_price": r.quotation_solo_price,
            "quotation_unit": r.quotation_unit,
            "quotation_compare": r.quotation_compare,
            "upper": r.upper,
            "description": r.description or ""
        })
    
    return {
        "id": str(price_compare.id),
        "creator": price_compare.creator,
        "description": price_compare.description or "",
        "created_at": price_compare.created_at,
        "updated_at": price_compare.updated_at,
        "resources": resource_list
    }