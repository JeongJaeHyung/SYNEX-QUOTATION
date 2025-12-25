# backend/api/v1/export/excel/schemas.py
from pydantic import BaseModel
from uuid import UUID

# 현재는 Path Parameter만 사용하므로 별도 스키마 불필요
# 향후 확장 시 사용

class ExcelExportRequest(BaseModel):
    """Excel Export 요청 (향후 확장용)"""
    quotation_type: str
    quotation_id: UUID