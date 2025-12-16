from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter()
router.mount("/static", StaticFiles(directory="frontend/static"), name="static")
router.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
templates = Jinja2Templates(directory="frontend")


@router.get("/", response_class=HTMLResponse)
async def quotation_comparison(request: Request):
    """
    견적 비교 페이지를 렌더링합니다.
    """
    return templates.TemplateResponse("template/quotation_comparison.html", {
        "request": request,
        "current_page": "quotation_comparison"
    })
