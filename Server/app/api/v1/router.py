# SYNEX+QUOTATION/Server/app/api/v1/router.py
from fastapi import APIRouter
from .parts.handler import handler as parts_handler
from .account.handler import handler as account_handler
from .quotation.router import router as quotation_router

router = APIRouter()

# Parts API 등록
router.include_router(parts_handler, prefix="/parts", tags=["Parts"])


# Account API 등록
router.include_router(account_handler, prefix="/accounts", tags=["Accounts"])

# Quotation API 등록 (추후 구현)
router.include_router(quotation_router, prefix="/quotation")
