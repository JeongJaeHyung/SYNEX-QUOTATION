from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# [변경] router 변수명을 handler로 변경했습니다.
handler = APIRouter()

templates = Jinja2Templates(directory="frontend")


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


# ==================== [신규 추가] 내정가 견적비교서 관련 라우터 ====================

@handler.get("/price_compare/register", response_class=HTMLResponse)
async def price_compare_register_sub(
    request: Request, 
    general_id: str = Query(..., description="연동할 General 프로젝트 ID")
):
    """
    내정가 견적비교서 생성 페이지 (Sub View)
    - General 상세 화면에서 호출되며, general_id를 필수로 받습니다.
    - 템플릿 파일명: price_compare_register_sub.html
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
    URL 예시: /service/quotation/general/price_compare/detail/UUID
    """
    return templates.TemplateResponse("template/quotation/general/price_compare_detail.html", {
        "request": request,
        "current_page": "quotation_default",
        "id": price_compare_id  # 템플릿에 ID 전달
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
    """상세 페이지 리다이렉트 (레거시)
    Note: 이 라우트는 가장 마지막에 배치해야 함 (동적 경로 때문)
    """
    return RedirectResponse(
        url=f"/service/quotation/default/form?mode=view&id={quotation_id}",
        status_code=302
    )