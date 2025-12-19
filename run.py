import sys
import os
import threading
import webview
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.core.config import templates, BASE_DIR

# 1. 경로 설정 (PyInstaller EXE 빌드 대응)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)  # EXE 실행 시 임시 폴더
else:
    BASE_DIR = Path(__file__).resolve().parent

# backend 폴더를 패키지 경로에 추가 (router 임포트용)
sys.path.insert(0, str(BASE_DIR))

# 2. FastAPI 앱 초기화
app = FastAPI(title="JLT Quotation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 정적 파일 및 템플릿 경로 설정 (frontend 폴더 기준)
FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
templates = Jinja2Templates(directory=str(FRONTEND_DIR))

# 4. 라우터 임포트 및 등록
# 주의: backend 폴더 안에 해당 파일들이 있어야 합니다.
from backend.service.router import router as service_router
from backend.api.router import router as api_router

app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])

# 5. 기본 페이지 라우팅 (main.py 로직 통합)
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("template/home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("template/login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("template/register.html", {"request": request})

@app.get("/quotation_detailed", response_class=HTMLResponse)
async def detailed_page(request: Request):
    return templates.TemplateResponse("template/quotation/general/quotation_detailed.html", {"request": request})

@app.get("/quotation_summary", response_class=HTMLResponse)
async def summary_page(request: Request):
    return templates.TemplateResponse("template/quotation/general/quotation_summary.html", {"request": request})

# 6. 실행 엔진
def run_fastapi():
    # 로컬 데스크톱 앱이므로 포트 8001 고정
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")

if __name__ == "__main__":
    # FastAPI 서버를 백그라운드 스레드에서 실행
    t = threading.Thread(target=run_fastapi, daemon=True)
    t.start()

    # pywebview 창 생성 및 실행
    webview.create_window(
        "JLT 견적 관리 시스템", 
        "http://127.0.0.1:8001",
        width=1280,
        height=800
    )
    
    # GUI 엔진 설정 (시스템 환경에 따라 'qt', 'gtk', 'cef' 등 선택 가능)
    # 특별한 설정이 없으면 자동으로 최적의 엔진을 찾습니다.
    webview.start()