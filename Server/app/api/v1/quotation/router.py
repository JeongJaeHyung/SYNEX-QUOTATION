# SYNEX+QUOTATION/Server/app/api/v1/router.py
from fastapi import APIRouter
from .general.handler import handler as general_handler
from .machine.handler import handler as machine_handler

router = APIRouter()

# Parts API 등록
router.include_router(general_handler, prefix="/general", tags=["General"])


# Machine API 등록
router.include_router(machine_handler, prefix="/machine", tags=["Machine"])
