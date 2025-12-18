# SYNEX+QUOTATION/Server/app/main.py
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from core.config import templates, BASE_DIR

from service.router import router as service_router
from api.router import router as api_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "frontend" / "static")), name="static")
app.mount("/assets", StaticFiles(directory=str(BASE_DIR / "frontend" / "assets")), name="assets")

templates = Jinja2Templates(directory=str(BASE_DIR / "frontend"))



@app.get("/")
async def root(request: Request):  # 1. 함수 인자에 request 추가
    return templates.TemplateResponse(
        "template/home.html", 
        {"request": request}       # 2. 컨텍스트 딕셔너리에 request 객체 전달 필수
    )






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

@app.get("/quotation_detailed", response_class=HTMLResponse)
async def register_page(request: Request):
    """을지"""
    return templates.TemplateResponse(
        "template/quotation/general/quotation_detailed.html",
        {"request": request}
    )

@app.get("/quotation_summary", response_class=HTMLResponse)
async def register_page(request: Request):
    """을지"""
    return templates.TemplateResponse(
        "template/quotation/general/quotation_summary.html",
        {"request": request}
    )



app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])