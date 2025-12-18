# SYNEX+QUOTATION/Server/app/service/part/router.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from main import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def parts(request: Request):
    return templates.TemplateResponse("template/part/parts_list_direct.html", {
        "request": request,
        "current_page": "part"
    })