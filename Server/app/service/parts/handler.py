# app/service/parts/handler.py
#
# 부품(Parts) 서비스 관련 API 엔드포인트 및 HTML 페이지 렌더링을 정의합니다.
# - 부품 목록 페이지를 제공하는 역할을 합니다.
#

from fastapi import APIRouter, Request # FastAPI 라우터, 요청 객체
from fastapi.responses import HTMLResponse # HTML 응답
from fastapi.staticfiles import StaticFiles # 정적 파일 서빙
from fastapi.templating import Jinja2Templates # Jinja2 템플릿 엔진

# API 라우터 인스턴스 생성
router = APIRouter()

# --- 정적 파일 및 템플릿 설정 ---
# 서비스 라우터 내에서만 사용되는 정적 파일과 템플릿 설정을 마운트합니다.
# 메인 앱(main.py)에서 이미 마운트되었더라도, 서브 라우터에서 특정 경로에 대해 다시 마운트할 수 있습니다.
router.mount("/static", StaticFiles(directory="frontend/static"), name="static")
router.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
templates = Jinja2Templates(directory="frontend")

@router.get("/", response_class=HTMLResponse)
async def parts_list_page(request: Request):
    """
    부품 목록 페이지를 렌더링하여 제공합니다.
    
    Args:
        request (Request): FastAPI 요청 객체.
        
    Returns:
        TemplateResponse: 'parts_list_direct.html' 템플릿을 렌더링한 HTML 응답.
    """
    return templates.TemplateResponse("template/parts_list_direct.html", {
        "request": request, # Jinja2 템플릿에서 request 객체에 접근할 수 있도록 전달
        "current_page": "parts" # 현재 페이지를 식별하기 위한 변수 (내비게이션 활성화 등)
    })