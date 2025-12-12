# SYNEX+QUOTATION/Server/app/api/v1/router.py
from fastapi import APIRouter
from .maker.handler import handler as maker_handler
from .part.handler import handler as part_handler
from .account.handler import handler as account_handler
from .quotation.router import router as quotation_router

router = APIRouter()



# Maker API 등록
router.include_router(maker_handler, prefix="/maker", tags=["Maker"])

# Parts API 등록
router.include_router(part_handler, prefix="/parts", tags=["Parts"])


# Account API 등록
router.include_router(account_handler, prefix="/account", tags=["Account"])

# Quotation API 등록 (추후 구현)
router.include_router(quotation_router, prefix="/quotation")
