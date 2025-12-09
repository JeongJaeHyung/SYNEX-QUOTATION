# SYNEX+QUOTATION/Server/app/api/v1/router.py
from fastapi import APIRouter
#from .default.handler import handler as default_handler
from .machine.handler import handler as machine_handler

router = APIRouter()

# Parts API 등록
#router.include_router(default_handler, prefix="/default", tags=["Default"])


# Machine API 등록
router.include_router(machine_handler, prefix="/machine", tags=["Machine"])
