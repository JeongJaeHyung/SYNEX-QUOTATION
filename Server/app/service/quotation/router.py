# SYNEX+QUOTATION/Server/app/view/quotation/router.py
from fastapi import APIRouter
from .machine.handler import handler as machine_handler
from .default.handler import router as default_handler

router = APIRouter()


@router.get("/")
async def root():
    return "Here is root, /service/quotation/"

router.include_router(machine_handler, prefix="/machine")
router.include_router(default_handler, prefix="/default")