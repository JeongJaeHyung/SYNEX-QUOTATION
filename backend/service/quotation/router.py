# SYNEX+QUOTATION/Server/app/service/quotation/router.py
from fastapi import APIRouter

from .general.handler import handler as general_handler
from .machine.handler import handler as machine_handler

router = APIRouter()


@router.get("/")
async def root():
    return "Here is root, /service/quotation/"


router.include_router(machine_handler, prefix="/machine")
router.include_router(general_handler, prefix="/general")
