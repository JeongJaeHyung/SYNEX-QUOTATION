# SYNEX+QUOTATION/Server/app/api/v1/router.py
from fastapi import APIRouter

from .excel.handler import handler as excel_handler
from .pdf.handler import handler as pdf_handler

router = APIRouter()

router.include_router(excel_handler, prefix="/excel", tags=["Excel"])
router.include_router(pdf_handler, prefix="/pdf", tags=["PDF"])
