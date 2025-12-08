# SYNEX+QUOTATION/Server/app/service/router.py
from fastapi import APIRouter
from .quotation.router import router as quotation_router
from .parts.handler import router as parts_handler

router = APIRouter()

@router.get("/")
async def root():
    return "Here is root, /service/"

router.include_router(quotation_router, prefix="/quotation")
router.include_router(parts_handler, prefix="/parts")