# app/service/quotation/machine/handler.py
#
# 장비 견적서(Machine Quotation) 관련 HTML 페이지 렌더링을 정의하는 핸들러 파일입니다.
# - 견적서 목록 페이지, 생성/조회/수정 통합 폼 페이지를 제공합니다.
# - 레거시 경로에 대한 리다이렉션도 처리합니다.
#

from fastapi import APIRouter, Request # FastAPI 라우터, 요청 객체
from fastapi.responses import HTMLResponse, RedirectResponse # HTML 응답, 리다이렉트 응답
from fastapi.templating import Jinja2Templates # Jinja2 템플릿 엔진

# API 라우터 인스턴스 생성
handler = APIRouter()
# Jinja2 템플릿 엔진 설정 (main.py와 동일하게 "frontend" 디렉토리 기준)
templates = Jinja2Templates(directory="frontend")

@handler.get("/", response_class=HTMLResponse)
async def machine_list_page(request: Request):
    """
    장비 견적서 목록 페이지를 렌더링하여 제공합니다.
    - '/service/quotation/machine' 경로로 접근합니다.
    
    Args:
        request (Request): FastAPI 요청 객체.
        
    Returns:
        TemplateResponse: 'machine_list_direct.html' 템플릿을 렌더링한 HTML 응답.
    """
    return templates.TemplateResponse("template/machine_list_direct.html", {
        "request": request, # Jinja2 템플릿에서 request 객체에 접근할 수 있도록 전달
        "current_page": "quotation_machine" # 현재 페이지를 식별하기 위한 변수 (내비게이션 활성화 등)
    })


@handler.get("/form", response_class=HTMLResponse)
async def machine_form_page(request: Request):
    """
    장비 견적서 생성/조회/수정 통합 폼 페이지를 렌더링하여 제공합니다.
    - 쿼리 파라미터 `mode`와 `id`를 통해 페이지의 동작 모드를 결정합니다.
    
    Query Parameters:
        mode (str): 페이지의 모드 ('create', 'view', 'edit'). 기본값은 'create'.
        id (UUID): 조회 또는 수정할 견적서의 ID (view, edit 모드에서 필수).
    
    Examples:
        - 새 견적서 생성: `/service/quotation/machine/form?mode=create`
        - 기존 견적서 조회: `/service/quotation/machine/form?mode=view&id=xxx`
        - 기존 견적서 수정: `/service/quotation/machine/form?mode=edit&id=xxx`
    
    Args:
        request (Request): FastAPI 요청 객체.
        
    Returns:
        TemplateResponse: 'machine_create.html' 템플릿을 렌더링한 HTML 응답.
    """
    return templates.TemplateResponse("template/machine_create.html", {
        "request": request,
        "current_page": "quotation_machine"
    })


# ============================================================
# 레거시 경로 리다이렉트 엔드포인트
# ============================================================
# 이전 버전 또는 다른 시스템에서 사용하던 URL 경로를 새로운 통합 폼 페이지로 리다이렉트합니다.

@handler.get("/create")
async def redirect_create_legacy(request: Request):
    """
    `/service/quotation/machine/create` 레거시 경로를 새로운 생성 폼 페이지로 리다이렉트합니다.
    """
    return RedirectResponse(
        url="/service/quotation/machine/form?mode=create",
        status_code=302 # 302 Found: 일시적 리다이렉트
    )


@handler.get("/{machine_id}")
async def redirect_view_legacy(machine_id: str):
    """
    `/service/quotation/machine/{machine_id}` 레거시 경로를 새로운 상세 조회 폼 페이지로 리다이렉트합니다.
    """
    return RedirectResponse(
        url=f"/service/quotation/machine/form?mode=view&id={machine_id}",
        status_code=302 # 302 Found: 일시적 리다이렉트
    )