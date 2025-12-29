# SYNEX+QUOTATION/Server/app/service/router.py
from fastapi import APIRouter

from .part.handler import router as part_handler
from .quotation.router import router as quotation_router

router = APIRouter()


@router.get("/")
async def root():
    return "Here is root, /service/"


router.include_router(quotation_router, prefix="/quotation")
router.include_router(part_handler, prefix="/part")  #
