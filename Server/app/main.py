# app/main.py
#
# SYNEX QUOTATION 시스템의 메인 FastAPI 애플리케이션 파일입니다.
# - FastAPI 앱 초기화 및 미들웨어 설정
# - 정적 파일(CSS, JS, 이미지) 마운트
# - Jinja2 템플릿 엔진 설정
# - 루트('/') 및 인증 관련 페이지(로그인, 회원가입) 라우트 정의
# - API 및 서비스 라우터를 포함
#

from pathlib import Path
import os
import sys

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 앱에 필요한 내부 모듈들이 `service`, `api`, `database` 등
# `app/` 하위에 있으므로 FastAPI가 시작될 때 경로를 먼저 등록합니다.
APP_ROOT = Path(__file__).resolve().parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

# 앱 디렉터리를 현재 작업 디렉터리로 설정하여 상대 경로(static, template 등)를 일관되게 사용합니다.
if os.getcwd() != str(APP_ROOT):
    os.chdir(str(APP_ROOT))

# API 및 서비스 라우터 임포트
from service.router import router as service_router
from api.router import router as api_router

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="SYNEX QUOTATION API",
    description="SYNEX QUOTATION 시스템을 위한 API 문서",
    version="1.0.0",
)

# CORS 미들웨어 설정
# 개발 환경에서 프론트엔드와 백엔드 간의 교차 출처 요청을 허용합니다.
# 실제 운영 환경에서는 allow_origins를 특정 도메인으로 제한해야 합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (개발용)
    allow_credentials=True, # 자격 증명(쿠키, HTTP 인증 등) 허용
    allow_methods=["*"],    # 모든 HTTP 메소드 허용 (GET, POST 등)
    allow_headers=["*"],    # 모든 HTTP 헤더 허용
)

# 정적/템플릿 기준 디렉토리
STATIC_DIR = APP_ROOT / "frontend" / "static"
ASSETS_DIR = APP_ROOT / "frontend" / "assets"
TEMPLATES_DIR = APP_ROOT / "frontend"

# 정적 파일 마운트
# 브라우저가 직접 접근할 수 있는 CSS, JS, 이미지 파일들을 서빙합니다.
# /static URL로 접근하면 frontend/static 디렉토리의 파일을 제공합니다.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
# /assets URL로 접근하면 frontend/assets 디렉토리의 파일을 제공합니다.
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# Jinja2 템플릿 엔진 설정
# "frontend" 디렉토리를 기준으로 HTML 템플릿 파일을 찾습니다.
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- 루트 및 인증 관련 HTML 페이지 라우트 ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    루트 경로 ('/')에 대한 HTML 응답을 제공합니다.
    시작 페이지 (홈 화면)를 렌더링합니다.
    """
    return templates.TemplateResponse(
        "template/home.html", # 렌더링할 템플릿 파일
        {"request": request}  # Jinja2 템플릿에서 request 객체에 접근할 수 있도록 전달
    )

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    로그인 페이지를 렌더링합니다.
    """
    return templates.TemplateResponse(
        "template/login.html",
        {"request": request}
    )

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """
    회원가입 페이지를 렌더링합니다.
    """
    return templates.TemplateResponse(
        "template/register.html",
        {"request": request}
    )

# --- 라우터 포함 ---
# 다른 모듈에서 정의된 API 및 서비스 라우터들을 메인 앱에 포함합니다.
# 이렇게 하면 코드를 모듈화하여 관리할 수 있습니다.

# API 라우터 포함 (예: /api/v1/parts, /api/v1/quotation 등)
# 모든 API 경로는 '/api' 접두사를 가집니다.
app.include_router(api_router, prefix="/api")
# 서비스 라우터 포함 (HTML 페이지를 제공하는 엔드포인트)
# 모든 서비스 경로는 '/service' 접두사를 가집니다.
app.include_router(service_router, prefix="/service", tags=["service"])
