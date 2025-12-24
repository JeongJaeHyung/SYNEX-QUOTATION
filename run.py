import os
import sys
import webview
import uvicorn
import threading
from pathlib import Path

# =======================================================================================================================================
# EXE 배포 설정 - Playwright 브라우저 경로
# =======================================================================================================================================

if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(APP_DIR / 'browsers')
else:
    APP_DIR = Path(__file__).parent

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.core.config import templates, BASE_DIR
from backend.service.router import router as service_router
from backend.api.router import router as api_router

# =======================================================================================================================================
# FAST API APPLICATION INITIALIZING SECTION
# =======================================================================================================================================

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

sys.path.insert(0, str(BASE_DIR))

FRONTEND_DIR = BASE_DIR / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

# =======================================================================================================================================
# API ROUTE SECTION
# =======================================================================================================================================

app.include_router(api_router, prefix="/api")
app.include_router(service_router, prefix="/service", tags=["service"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("template/home.html", {"request": request})

@app.get("/quotation_detailed", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("template/quotation/general/quotation_detailed.html", {"request":request})

# =======================================================================================================================================
# RUN
# =======================================================================================================================================

def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    t = threading.Thread(target=run_fastapi, daemon=True)
    t.start()

    webview.create_window(
        "JLT 견적 관리 시스템",
        "http://127.0.0.1:8000",
        width=1280,
        height=800,
        confirm_close=True
    )

    webview.start()
