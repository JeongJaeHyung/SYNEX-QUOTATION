# app/service/quotation/router.py
#
# 견적(Quotation) 서비스 관련 라우트들을 통합 관리하는 파일입니다.
# - 장비 견적서, 일반 견적서 등 견적과 관련된 모든 하위 서비스 라우터를 여기에 연결합니다.
#

from fastapi import APIRouter # FastAPI 라우터 인스턴스 생성을 위함
# 하위 라우터들을 임포트합니다.
from .machine.handler import handler as machine_handler # 장비 견적서 관련 핸들러 (라우터 역할)
from .default.handler import router as default_handler # 일반 견적서 관련 핸들러 (라우터 역할)

# 견적 서비스 라우터 인스턴스 생성
router = APIRouter()

@router.get("/")
async def root():
    """
    견적 서비스 루트 경로('/')에 대한 기본 응답을 제공합니다.
    (개발 또는 테스트용으로 사용될 수 있습니다.)
    """
    return "견적 서비스 루트입니다. /service/quotation/"

# --- 하위 라우터 포함 ---
# 각 견적 유형의 라우터를 메인 견적 서비스 라우터에 연결하여 URL 구조를 정의합니다.

# 장비 견적서 관련 핸들러를 '/machine' 접두사로 포함합니다.
# 예: /service/quotation/machine, /service/quotation/machine/form
router.include_router(machine_handler, prefix="/machine")

# 일반 견적서 관련 핸들러를 '/default' 접두사로 포함합니다.
# 예: /service/quotation/default, /service/quotation/default/form
router.include_router(default_handler, prefix="/default")
