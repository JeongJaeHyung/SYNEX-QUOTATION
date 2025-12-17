# SYNEX+QUOTATION/Server/app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from service.router import router as service_router
from api.router import router as api_router
from utils.path_utils import get_resource_path


# ============================================================
# FastAPI 앱 설정
# ============================================================
app = FastAPI(
    title="SYNEX+ 견적 시스템",
    description="산업용 장비 견적 관리 시스템",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 정적 파일 및 템플릿 설정 (PyInstaller 호환)
# ============================================================
STATIC_DIR = get_resource_path("frontend/static")
ASSETS_DIR = get_resource_path("frontend/assets")
TEMPLATES_DIR = get_resource_path("frontend")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

templates = Jinja2Templates(directory=TEMPLATES_DIR)


# ============================================================
# 페이지 라우트
# ============================================================
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "template/home.html",
        {"request": request}
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
async def quotation_detailed_page(request: Request):
    """견적 상세 페이지"""
    return templates.TemplateResponse(
        "template/quotation/general/quotation_detailed.html",
        {"request": request}
    )

@app.get("/quotation_summary", response_class=HTMLResponse)
async def quotation_summary_page(request: Request):
    """견적 요약 페이지"""
    return templates.TemplateResponse(
        "template/quotation/general/quotation_summary.html",
        {"request": request}
    )


# ============================================================
# API 라우터 등록
# ============================================================
app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])
