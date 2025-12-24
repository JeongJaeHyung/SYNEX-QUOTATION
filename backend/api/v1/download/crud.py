# backend/api/v1/download/crud.py
import os
import sys
import json
import ctypes
import subprocess
import re
from pathlib import Path
from ctypes import wintypes
from playwright.async_api import async_playwright


# =======================================================================================================================================
# 경로 설정
# =======================================================================================================================================

if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).parent
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(APP_DIR / 'browsers')
else:
    APP_DIR = Path(__file__).parent.parent.parent.parent.parent  # backend -> s-q

SETTINGS_FILE = APP_DIR / 'settings.json'


# =======================================================================================================================================
# Windows API 상수 및 구조체
# =======================================================================================================================================

OFN_OVERWRITEPROMPT = 0x00000002
OFN_NOCHANGEDIR = 0x00000008
OFN_EXPLORER = 0x00080000
BIF_RETURNONLYFSDIRS = 0x00000001
BIF_NEWDIALOGSTYLE = 0x00000040


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


# =======================================================================================================================================
# Windows 대화상자 함수
# =======================================================================================================================================

def get_save_file_path(default_filename: str, initial_dir: str = None) -> str:
    """Windows 파일 저장 대화상자"""
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
    """Windows 폴더 선택 대화상자"""
    shell32 = ctypes.windll.shell32
    ole32 = ctypes.windll.ole32

    ole32.CoInitialize(None)

    try:
        pidl = shell32.SHBrowseForFolderW(ctypes.byref(
            ctypes.create_string_buffer(
                b'\x00' * 64 +
                "PDF 저장 폴더 선택".encode('utf-16-le') +
                b'\x00' * 200
            )
        ))

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

def get_default_save_path() -> str:
    """현재 사용자의 기본 저장 경로"""
    return str(Path.home() / "Documents" / "JLT_견적서")


def load_settings() -> dict:
    """설정 파일 로드"""
    default_path = get_default_save_path()
    default_settings = {
        "pdfSavePath": default_path,
        "askSaveLocation": False
    }

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = {**default_settings, **json.load(f)}

            # 저장 경로가 유효하지 않으면 현재 사용자의 기본 경로로 대체
            saved_path = Path(settings.get("pdfSavePath", ""))
            if not saved_path.parent.exists():
                settings["pdfSavePath"] = default_path
                save_settings_to_file(settings)

            return settings
        except:
            pass

    save_settings_to_file(default_settings)
    return default_settings


def save_settings_to_file(settings: dict):
    """설정 파일 저장"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


# =======================================================================================================================================
# PDF 생성
# =======================================================================================================================================

async def generate_pdf(url: str, file_path: str) -> None:
    """Playwright로 PDF 생성"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, wait_until="networkidle")

        await page.pdf(
            path=file_path,
            format="A4",
            print_background=True,
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"}
        )

        await browser.close()


def open_file_in_explorer(file_path: str):
    """탐색기에서 파일 선택하여 열기"""
    subprocess.Popen(f'explorer /select,"{file_path}"', shell=True)


def sanitize_filename(text: str, default: str = "") -> str:
    """파일명에서 특수문자 제거"""
    if not text:
        return default
    return re.sub(r'[\/*?:"<>|]', '_', text)
