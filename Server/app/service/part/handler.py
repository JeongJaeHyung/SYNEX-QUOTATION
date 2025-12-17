# SYNEX+QUOTATION/Server/app/service/part/router.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from utils.path_utils import get_resource_path

router = APIRouter()
router.mount("/static", StaticFiles(directory=get_resource_path("frontend/static")), name="static")
router.mount("/assets", StaticFiles(directory=get_resource_path("frontend/assets")), name="assets")
templates = Jinja2Templates(directory=get_resource_path("frontend"))


@router.get("/", response_class=HTMLResponse)
async def parts(request: Request):
    return templates.TemplateResponse("template/part/parts_list_direct.html", {
        "request": request,
        "current_page": "part"
    })