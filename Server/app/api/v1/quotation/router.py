# SYNEX+QUOTATION/Server/app/api/v1/router.py
from fastapi import APIRouter
from .general.handler import handler as general_handler
from .price_compare.handler import handler as price_compare_handler
from .machine.handler import handler as machine_handler

router = APIRouter()



# General API 등록
router.include_router(general_handler, prefix="/general", tags=["General"])

# General API 등록
router.include_router(price_compare_handler, prefix="/price_compare", tags=["Price_compare"])

# Machine API 등록
router.include_router(machine_handler, prefix="/machine", tags=["Machine"])
