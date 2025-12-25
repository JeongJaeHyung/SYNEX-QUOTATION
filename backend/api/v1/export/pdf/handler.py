# backend/api/v1/download/handler.py
import asyncio
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .schemas import SettingsModel, PDFSaveRequest
from .crud import (
    load_settings,
    save_settings_to_file,
    get_folder_path,
    get_save_file_path,
    generate_pdf,
    open_file_in_explorer,
    sanitize_filename
)

handler = APIRouter()


# =======================================================================================================================================
# 설정 API
# =======================================================================================================================================

@handler.get("/settings")
async def get_settings():
    """설정 조회"""
    return JSONResponse(load_settings())


@handler.post("/settings")
async def update_settings(settings: SettingsModel):
    """설정 저장"""
    save_settings_to_file(settings.model_dump())
    return JSONResponse({"success": True})


@handler.get("/select-folder")
async def select_folder():
    """폴더 선택 대화상자"""
    loop = asyncio.get_event_loop()
    folder_path = await loop.run_in_executor(None, get_folder_path)

    if folder_path:
        return JSONResponse({"success": True, "path": folder_path})
    return JSONResponse({"success": False, "path": ""})


# =======================================================================================================================================
# PDF 저장 API
# =======================================================================================================================================

@handler.post("/save-pdf")
async def save_pdf_endpoint(request: PDFSaveRequest):
    """PDF 파일 저장 - Playwright로 인쇄 레이아웃 적용"""
    try:
        settings = load_settings()
        base_path = settings.get("pdfSavePath") or str(Path.home() / "Documents" / "JLT_견적서")
        ask_location = settings.get("askSaveLocation", False)

        safe_project = sanitize_filename(request.projectName, '기타')
        safe_doctype = sanitize_filename(request.docType, '문서')
        safe_filename = sanitize_filename(request.filename)

        if ask_location:
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(
                None,
                lambda: get_save_file_path(safe_filename, base_path)
            )

            if not file_path:
                return JSONResponse({"success": False, "message": "저장이 취소되었습니다."})
        else:
            save_dir = Path(base_path) / safe_doctype
            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = str(save_dir / safe_filename)

        print(f"[PDF] Starting: {request.url}")

        await generate_pdf(request.url, file_path)

        print(f"[PDF] File created: {file_path}")

        if not ask_location:
            open_file_in_explorer(file_path)

        return JSONResponse({"success": True, "path": file_path})
    except Exception as e:
        print(f"[PDF] Error: {str(e)}")
        return JSONResponse({"success": False, "message": str(e)})