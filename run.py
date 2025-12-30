import ctypes
import json
import os
import subprocess
import sys
import threading
from ctypes import wintypes
from pathlib import Path

import uvicorn
import webview

# =======================================================================================================================================
# EXE 배포 설정 - Playwright 브라우저 경로
# =======================================================================================================================================

# PyInstaller로 빌드된 exe인지 확인
if getattr(sys, "frozen", False):
    # exe 실행 시: exe 파일이 있는 폴더 기준
    APP_DIR = Path(sys.executable).parent
    # Playwright 브라우저 경로를 exe 폴더 내 browsers로 설정
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(APP_DIR / "browsers")
else:
    # 개발 모드: 스크립트 파일 기준
    APP_DIR = Path(__file__).parent

# 설정 파일 경로
SETTINGS_FILE = APP_DIR / "settings.json"

# =======================================================================================================================================
# Windows API 파일/폴더 대화상자 (스레드 안전)
# =======================================================================================================================================

# Windows API 상수
OFN_OVERWRITEPROMPT = 0x00000002
OFN_NOCHANGEDIR = 0x00000008
OFN_EXPLORER = 0x00080000
BIF_RETURNONLYFSDIRS = 0x00000001
BIF_NEWDIALOGSTYLE = 0x00000040


# Windows API 구조체
class OPENFILENAME(ctypes.Structure):
    _fields_ = [
        ("lStructSize", wintypes.DWORD),
        ("hwndOwner", wintypes.HWND),
        ("hInstance", wintypes.HINSTANCE),
        ("lpstrFilter", wintypes.LPCWSTR),
        ("lpstrCustomFilter", wintypes.LPWSTR),
        ("nMaxCustFilter", wintypes.DWORD),
        ("nFilterIndex", wintypes.DWORD),
        ("lpstrFile", wintypes.LPWSTR),
        ("nMaxFile", wintypes.DWORD),
        ("lpstrFileTitle", wintypes.LPWSTR),
        ("nMaxFileTitle", wintypes.DWORD),
        ("lpstrInitialDir", wintypes.LPCWSTR),
        ("lpstrTitle", wintypes.LPCWSTR),
        ("Flags", wintypes.DWORD),
        ("nFileOffset", wintypes.WORD),
        ("nFileExtension", wintypes.WORD),
        ("lpstrDefExt", wintypes.LPCWSTR),
        ("lCustData", wintypes.LPARAM),
        ("lpfnHook", ctypes.c_void_p),
        ("lpTemplateName", wintypes.LPCWSTR),
        ("pvReserved", ctypes.c_void_p),
        ("dwReserved", wintypes.DWORD),
        ("FlagsEx", wintypes.DWORD),
    ]


def get_save_file_path(default_filename: str, initial_dir: str = None) -> str:
    """Windows 파일 저장 대화상자 (스레드 안전)"""
    comdlg32 = ctypes.windll.comdlg32

    buffer = ctypes.create_unicode_buffer(default_filename, 260)

    ofn = OPENFILENAME()
    ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
    ofn.lpstrFilter = "PDF 파일\0*.pdf\0모든 파일\0*.*\0"
    ofn.lpstrFile = ctypes.cast(buffer, wintypes.LPWSTR)
    ofn.nMaxFile = 260
    ofn.lpstrInitialDir = initial_dir if initial_dir else None
    ofn.lpstrTitle = "PDF 저장 위치 선택"
    ofn.Flags = OFN_OVERWRITEPROMPT | OFN_EXPLORER | OFN_NOCHANGEDIR
    ofn.lpstrDefExt = "pdf"

    if comdlg32.GetSaveFileNameW(ctypes.byref(ofn)):
        return buffer.value
    return None


def get_folder_path() -> str:
    """Windows 폴더 선택 대화상자 (스레드 안전)"""
    shell32 = ctypes.windll.shell32
    ole32 = ctypes.windll.ole32

    ole32.CoInitialize(None)

    try:
        pidl = shell32.SHBrowseForFolderW(
            ctypes.byref(
                ctypes.create_string_buffer(
                    b"\x00" * 64
                    + "PDF 저장 폴더 선택".encode("utf-16-le")
                    + b"\x00" * 200
                )
            )
        )

        if pidl:
            path_buffer = ctypes.create_unicode_buffer(260)
            shell32.SHGetPathFromIDListW(pidl, path_buffer)
            ole32.CoTaskMemFree(pidl)
            return path_buffer.value
    finally:
        ole32.CoUninitialize()

    return None


# =======================================================================================================================================
# 설정 관리
# =======================================================================================================================================


def load_settings() -> dict:
    """설정 파일 로드 (없으면 자동 생성)"""
    default_settings = {
        "pdfSavePath": str(Path.home() / "Documents" / "JLT_견적서"),
        "askSaveLocation": False,
    }

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                return {**default_settings, **json.load(f)}
        except:
            pass

    # 설정 파일이 없으면 기본값으로 자동 생성
    save_settings_to_file(default_settings)
    return default_settings


def save_settings_to_file(settings: dict):
    """설정 파일 저장"""
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright
from pydantic import BaseModel

from backend.api.router import router as api_router

# backend 폴더의 설정을 그대로 가져옵니다.
from backend.core.config import BASE_DIR, templates
from backend.service.router import router as service_router

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


@app.get("/quotation_detailed", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "template/quotation/general/quotation_detailed.html", {"request": request}
    )


# =======================================================================================================================================
# 설정 API
# =======================================================================================================================================


class SettingsModel(BaseModel):
    pdfSavePath: str = ""
    askSaveLocation: bool = False


@app.get("/api/settings")
async def get_settings():
    """설정 조회"""
    return JSONResponse(load_settings())


@app.post("/api/settings")
async def update_settings(settings: SettingsModel):
    """설정 저장"""
    save_settings_to_file(settings.model_dump())
    return JSONResponse({"success": True})


@app.get("/api/select-folder")
async def select_folder():
    """폴더 선택 대화상자"""
    import asyncio

    # 별도 스레드에서 폴더 선택 대화상자 실행
    loop = asyncio.get_event_loop()
    folder_path = await loop.run_in_executor(None, get_folder_path)

    if folder_path:
        return JSONResponse({"success": True, "path": folder_path})
    return JSONResponse({"success": False, "path": ""})


# =======================================================================================================================================
# PDF 저장 API (Playwright 사용)
# =======================================================================================================================================


class PDFSaveRequest(BaseModel):
    url: str
    filename: str
    projectName: str = ""
    docType: str = ""
    generalName: str = ""
    folderTitle: str = ""


@app.post("/api/save-pdf")
async def save_pdf_endpoint(request: PDFSaveRequest):
    """PDF 파일 저장 - Playwright로 인쇄 레이아웃 적용"""
    import asyncio
    import re

    try:
        # 설정 로드
        settings = load_settings()
        base_path = settings.get("pdfSavePath") or str(
            Path.home() / "Documents" / "JLT_견적서"
        )
        ask_location = settings.get("askSaveLocation", False)

        # 파일명에서 특수문자 제거
        safe_doctype = (
            re.sub(r'[\\/*?:"<>|]', "_", request.docType) if request.docType else "문서"
        )
        safe_folder_title = (
            re.sub(r'[\\/*?:"<>|]', "_", request.folderTitle) if request.folderTitle else ""
        )
        safe_general_name = (
            re.sub(r'[\\/*?:"<>|]', "_", request.generalName) if request.generalName else ""
        )
        safe_filename = re.sub(r'[\\/*?:"<>|]', "_", request.filename)

        if ask_location:
            # 수동 저장: 파일 대화상자 열기
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(
                None, lambda: get_save_file_path(safe_filename, base_path)
            )

            if not file_path:
                return JSONResponse(
                    {"success": False, "message": "저장이 취소되었습니다."}
                )
        else:
            # 자동 저장: 개별 PDF export는 항상 /{general.name}/{folder.title}/PDF/
            if safe_general_name and safe_folder_title:
                # 개별 저장: /{general.name}/{folder.title}/PDF/
                save_dir = Path(base_path) / safe_general_name / safe_folder_title / "PDF"
            elif safe_general_name:
                # Fallback: 폴더명 없는 경우 /{general.name}/PDF/
                save_dir = Path(base_path) / safe_general_name / "PDF"
            else:
                # Fallback: general.name도 없는 경우
                save_dir = Path(base_path) / "PDF"

            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = str(save_dir / safe_filename)

        print(f"[PDF] Starting: {request.url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 페이지 로드
            await page.goto(request.url, wait_until="networkidle")

            # PDF 생성 (A4 사이즈, 인쇄 CSS 적용)
            await page.pdf(
                path=file_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "10mm",
                    "bottom": "10mm",
                    "left": "10mm",
                    "right": "10mm",
                },
            )

            await browser.close()

        print(f"[PDF] File created: {file_path}")

        # 자동 저장인 경우 폴더 열기
        if not ask_location:
            subprocess.Popen(f'explorer /select,"{file_path}"', shell=True)

        return JSONResponse({"success": True, "path": file_path})
    except Exception as e:
        print(f"[PDF] Error: {str(e)}")
        return JSONResponse({"success": False, "message": str(e)})


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
        confirm_close=True,
    )

    # GUI 엔진 자동 선택
    webview.start()
