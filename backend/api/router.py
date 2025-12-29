# SYNEX+QUOTATION/Server/app/api/router.py
from fastapi import APIRouter

from .v1.router import router as v1_router

router = APIRouter()

# v1 API 등록
router.include_router(v1_router, prefix="/v1")

# v2 API는 추후 구현
