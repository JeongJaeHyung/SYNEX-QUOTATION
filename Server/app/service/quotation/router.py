# SYNEX+QUOTATION/Server/app/service/quotation/router.py
from fastapi import APIRouter
from .machine.handler import handler as machine_handler
from .general.handler import router as general_handler

router = APIRouter()


@router.get("/")
async def root():
    return "Here is root, /service/quotation/"

router.include_router(machine_handler, prefix="/machine")
router.include_router(general_handler, prefix="/general")