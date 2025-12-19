import os
import sys
import webview
import uvicorn
import threading
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# backend 폴더의 설정을 그대로 가져옵니다.
from backend.core.config import templates, BASE_DIR
from backend.service.router import router as service_router
from backend.api.router import router as api_router

# =======================================================================================================================================
# FAST API APPLICATION INITIALIZING SECTION
# =======================================================================================================================================

# redirect_slashes=False를 추가하여 /api/machine/ 같은 요청도 /api/machine으로 매끄럽게 연결합니다.
app = FastAPI(title="JLT Quotation System", redirect_slashes=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================================================================================================================================
# DIR SET SECTION
# =======================================================================================================================================

# backend를 패키지로 인식하게 하기 위한 경로 추가
sys.path.insert(0, str(BASE_DIR))

FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

# templates는 backend.core.config에서 이미 정의된 것을 사용하므로 중복 선언하지 않아도 됩니다.

# =======================================================================================================================================
# API ROUTE SECTION
# =======================================================================================================================================

app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("template/home.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("template/login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("template/register.html", {"request": request})

# =======================================================================================================================================
# PY WEB VIEW, SET AND RUN SECTION
# =======================================================================================================================================

def run_fastapi():
    # log_level="info"를 유지하여 DB 연결 경로 등을 터미널에서 계속 모니터링합니다.
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    # 서버 기동
    t = threading.Thread(target=run_fastapi, daemon=True)
    t.start()   

    # 앱 창 생성
    webview.create_window(
        "JLT 견적 관리 시스템", 
        "http://127.0.0.1:8000",
        width=1280,
        height=800,
        confirm_close=True # 창 닫을 때 확인창 띄우기 (옵션)
    )
    
    # 리눅스 환경에서 GTK 에러 방지를 위해 GUI 엔진 자동 선택을 맡깁니다.
    webview.start(gui='qt')