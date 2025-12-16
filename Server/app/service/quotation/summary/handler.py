# SYNEX+QUOTATION/Server/app/service/quotation/summary/handler.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter()
router.mount("/static", StaticFiles(directory="frontend/static"), name="static")
router.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
templates = Jinja2Templates(directory="frontend")


@router.get("/", response_class=HTMLResponse)
async def quotation_summary(request: Request):
    return templates.TemplateResponse("template/quotation_summary.html", {
        "request": request,
        "current_page": "quotation_summary"
    })
