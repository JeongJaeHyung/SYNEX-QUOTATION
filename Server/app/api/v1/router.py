# SYNEX+QUOTATION/Server/app/api/v1/router.py
from fastapi import APIRouter
from .parts.handler import router as parts_router
#from .quotation.router import router as quotation_router

router = APIRouter()

# Parts API 등록
router.include_router(parts_router, prefix="/parts", tags=["Parts"])

"""
# Quotation API 등록 (추후 구현)
router.include_router(
    quotation_router,
    prefix="/quotation",
    tags=["Quotation"]
)
"""