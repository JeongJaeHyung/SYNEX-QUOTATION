# SYNEX+QUOTATION/Server/app/main.py
from pathlib import Path

from api.router import router as api_router
from core.config import BASE_DIR, templates
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from service.router import router as service_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "frontend" / "static")),
    name="static",
)
app.mount(
    "/assets",
    StaticFiles(directory=str(BASE_DIR / "frontend" / "assets")),
    name="assets",
)
templates = Jinja2Templates(directory=str(BASE_DIR / "frontend"))


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("template/home.html", {"request": request})


'''
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """로그인 페이지"""
    return templates.TemplateResponse(
        "template/login.html",
        {"request": request}
    )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """회원가입 페이지"""
    return templates.TemplateResponse(
        "template/register.html",
        {"request": request}
    )

'''


@app.get("/quotation_detailed", response_class=HTMLResponse)
async def register_page(request: Request):
    """을지"""
    return templates.TemplateResponse(
        "template/quotation/general/quotation_detailed.html", {"request": request}
    )


@app.get("/quotation_summary", response_class=HTMLResponse)
async def register_page(request: Request):
    """을지"""
    return templates.TemplateResponse(
        "template/quotation/general/quotation_summary.html", {"request": request}
    )


app.include_router(api_router, prefix="/api")

app.include_router(service_router, prefix="/service", tags=["service"])
