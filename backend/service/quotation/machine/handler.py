# SYNEX+QUOTATION/Server/app/service/quotation/machine/handler.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from backend.core.config import templates

handler = APIRouter()

@handler.get("/", response_class=HTMLResponse)
async def machine_list(request: Request):
    """장비 견적서 목록 페이지"""
    return templates.TemplateResponse("template/quotation/machine/machine_list_direct.html", {
        "request": request,
        "current_page": "quotation_machine"
    })


@handler.get("/form", response_class=HTMLResponse)
async def machine_form(request: Request):
    """생성/조회/수정 통합 페이지
    
    Query Parameters:
        mode: create | view | edit (default: create)
        id: UUID (view, edit 모드에서 필수)
    
    Examples:
        /service/quotation/machine/form?mode=create
        /service/quotation/machine/form?mode=view&id=xxx
        /service/quotation/machine/form?mode=edit&id=xxx
    """
    return templates.TemplateResponse("template/quotation/machine/machine_create.html", {
        "request": request,
        "current_page": "quotation_machine"
    })


# ==================== 레거시 경로 리다이렉트 ====================

@handler.get("/create")
async def redirect_create(request: Request):
    """생성 페이지 리다이렉트 (레거시)"""
    return RedirectResponse(
        url="/service/quotation/machine/form?mode=create",
        status_code=302
    )


@handler.get("/{machine_id}")
async def redirect_view(machine_id: str):
    """상세 페이지 리다이렉트 (레거시)"""
    return RedirectResponse(
        url=f"/service/quotation/machine/form?mode=view&id={machine_id}",
        status_code=302
    )