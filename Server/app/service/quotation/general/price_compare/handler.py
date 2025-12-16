# service/quotation/default/handler.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="frontend")


@router.get("/", response_class=HTMLResponse)
async def default_list(request: Request):
    """견적서(일반) 목록 페이지"""
    return templates.TemplateResponse("template/default_list.html", {
        "request": request,
        "current_page": "quotation_default"
    })


@router.get("/form", response_class=HTMLResponse)
async def default_form(request: Request):
    """생성/조회/수정 통합 페이지
    
    Query Parameters:
        mode: create | view | edit (default: create)
        id: UUID (view, edit 모드에서 필수)
    
    Examples:
        /service/quotation/default/form?mode=create
        /service/quotation/default/form?mode=view&id=xxx
        /service/quotation/default/form?mode=edit&id=xxx
    """
    return templates.TemplateResponse("template/default_create.html", {
        "request": request,
        "current_page": "quotation_default"
    })


# ==================== 레거시 경로 리다이렉트 ====================

@router.get("/create")
async def redirect_create(request: Request):
    """생성 페이지 리다이렉트 (레거시)"""
    return RedirectResponse(
        url="/service/quotation/default/form?mode=create",
        status_code=302
    )


@router.get("/{quotation_id}")
async def redirect_view(quotation_id: str):
    """상세 페이지 리다이렉트 (레거시)
    
    Note: 이 라우트는 가장 마지막에 배치해야 함
    """
    return RedirectResponse(
        url=f"/service/quotation/default/form?mode=view&id={quotation_id}",
        status_code=302
    )