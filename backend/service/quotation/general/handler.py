from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from backend.core.config import templates

# [변경] router 변수명을 handler로 변경했습니다.
handler = APIRouter()

@handler.get("/", response_class=HTMLResponse)
async def default_list(request: Request):
    """견적서(일반) 목록 페이지"""
    return templates.TemplateResponse("template/quotation/general/default_list.html", {
        "request": request,
        "current_page": "quotation_default"
    })


@handler.get("/form", response_class=HTMLResponse)
async def default_form(request: Request):
    """생성/조회/수정 통합 페이지"""
    return templates.TemplateResponse("template/quotation/general/default_create.html", {
        "request": request,
        "current_page": "quotation_default"
    })


# ==================== 내정가 견적비교서 관련 라우터 ====================

@handler.get("/price_compare/register", response_class=HTMLResponse)
async def price_compare_register_sub(
    request: Request, 
    general_id: str = Query(..., description="연동할 General 프로젝트 ID")
):
    """
    내정가 견적비교서 생성 페이지 (Sub View)
    - General 상세 화면에서 호출되며, general_id를 필수로 받습니다.
    """
    return templates.TemplateResponse("template/quotation/general/price_compare_register_sub.html", {
        "request": request,
        "current_page": "quotation_default",
        "general_id": general_id
    })


@handler.get("/price_compare/detail/{price_compare_id}", response_class=HTMLResponse)
async def price_compare_detail_view(request: Request, price_compare_id: str):
    """
    내정가 견적비교서 상세 화면 (View & Edit)
    """
    return templates.TemplateResponse("template/quotation/general/price_compare_detail.html", {
        "request": request,
        "current_page": "quotation_default",
        "id": price_compare_id
    })


# ==================== [수정] 견적서(을지) 관련 라우터 ====================

@handler.get("/detailed/register", response_class=HTMLResponse)
async def detailed_register_view(
    request: Request, 
    general_id: str = Query(..., description="연동할 General 프로젝트 ID")
):
    """
    [신규 추가] 상세 견적서(을지) 생성 페이지
    - 내정가 비교표를 선택하여 을지를 생성하는 화면
    - URL: /service/quotation/general/detailed/register?general_id=UUID
    """
    return templates.TemplateResponse("template/quotation/general/detailed_register.html", {
        "request": request,
        "current_page": "quotation_default",
        "general_id": general_id
    })


@handler.get("/detailed/detail/{detailed_id}", response_class=HTMLResponse)
async def detailed_view(request: Request, detailed_id: str):
    """
    견적서(을지) 상세 화면 (조회 및 수정)
    """
    return templates.TemplateResponse("template/quotation/general/quotation_detailed.html", {
        "request": request,
        "current_page": "quotation_default",
        "id": detailed_id
    })


# ==================== 견적서(갑지) 관련 라우터 ====================

@handler.get("/header/detail/{header_id}", response_class=HTMLResponse)
async def header_view(request: Request, header_id: str):
    """
    견적서(갑지) 상세 화면
    """
    return templates.TemplateResponse("template/quotation/general/quotation_summary.html", {
        "request": request,
        "current_page": "quotation_default",
        "id": header_id
    })

@handler.get("/header/register", response_class=HTMLResponse)
async def header_register_view(
    request: Request, 
    general_id: str = Query(..., description="연동할 General 프로젝트 ID")
):
    """
    [명칭 수정] 견적서(갑지) 생성 페이지
    - URL: /service/quotation/general/header/register?general_id=UUID
    """
    return templates.TemplateResponse("template/quotation/general/header_register.html", {
        "request": request,
        "current_page": "quotation_default",
        "general_id": general_id
    })


# ==================== 레거시 경로 리다이렉트 ====================

@handler.get("/create")
async def redirect_create(request: Request):
    """생성 페이지 리다이렉트 (레거시)"""
    return RedirectResponse(
        url="/service/quotation/default/form?mode=create",
        status_code=302
    )


@handler.get("/{quotation_id}")
async def redirect_view(quotation_id: str):
    """상세 페이지 리다이렉트 (레거시)"""
    return RedirectResponse(
        url=f"/service/quotation/default/form?mode=view&id={quotation_id}",
        status_code=302
    )


@handler.get("/compare/form", response_class=HTMLResponse)
def price_compare_form(request: Request):
    return templates.TemplateResponse("quotation/general/price_compare_detail.html", {"request": request})