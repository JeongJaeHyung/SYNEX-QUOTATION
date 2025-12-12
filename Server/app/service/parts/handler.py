# SYNEX+QUOTATION/Server/app/service/parts/router.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter()
router.mount("/static", StaticFiles(directory="frontend/static"), name="static")
router.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")
templates = Jinja2Templates(directory="frontend")


@router.get("/", response_class=HTMLResponse)
async def parts(request: Request):
    return templates.TemplateResponse("template/parts_list_direct.html", {
        "request": request,
        "current_page": "parts"
    })