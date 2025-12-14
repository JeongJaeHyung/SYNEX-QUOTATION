# app/service/router.py
#
# 서비스 관련 라우트들을 통합 관리하는 메인 라우터 파일입니다.
# - 주로 HTML 페이지를 렌더링하여 제공하는 엔드포인트들을 포함합니다.
# - 각 서비스 영역(예: 견적, 부품)의 하위 라우터들을 메인 서비스 라우터에 연결합니다.
#

from fastapi import APIRouter # FastAPI 라우터 인스턴스 생성을 위함
# 하위 라우터들을 임포트합니다.
from .quotation.router import router as quotation_router # 견적 관련 서비스 라우터
from .parts.handler import router as parts_handler # 부품 관련 서비스 핸들러 (직접 라우터)

# 메인 서비스 라우터 인스턴스 생성
router = APIRouter()

@router.get("/")
async def root():
    """
    서비스 루트 경로('/')에 대한 기본 응답을 제공합니다.
    (개발 또는 테스트용으로 사용될 수 있습니다.)
    """
    return "서비스 루트입니다. /service/"

# --- 하위 라우터 포함 ---
# 각 서비스 영역의 라우터를 메인 서비스 라우터에 연결하여 URL 구조를 정의합니다.

# 견적(quotation) 관련 라우터를 '/quotation' 접두사로 포함합니다.
# 예: /service/quotation/machine, /service/quotation/default
router.include_router(quotation_router, prefix="/quotation")

# 부품(parts) 관련 핸들러(라우터)를 '/parts' 접두사로 포함합니다.
# 예: /service/parts
router.include_router(parts_handler, prefix="/parts")