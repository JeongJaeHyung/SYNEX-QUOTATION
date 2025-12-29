# backend/api/v1/download/handler.py
import asyncio
from datetime import datetime
from io import BytesIO
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from backend.database import get_db

from .crud import (
    generate_pdf,
    generate_pdf_bytes,
    get_folder_path,
    get_save_file_path,
    load_settings,
    open_file_in_explorer,
    sanitize_filename,
    save_settings_to_file,
)
from .schemas import PDFSaveRequest, SettingsModel

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
        base_path = settings.get("pdfSavePath") or str(
            Path.home() / "Documents" / "JLT_견적서"
        )
        ask_location = settings.get("askSaveLocation", False)

        sanitize_filename(request.projectName, "기타")
        safe_doctype = sanitize_filename(request.docType, "문서")
        safe_filename = sanitize_filename(request.filename)

        if ask_location:
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(
                None, lambda: get_save_file_path(safe_filename, base_path)
            )

            if not file_path:
                return JSONResponse(
                    {"success": False, "message": "저장이 취소되었습니다."}
                )
        else:
            # 💡 견적서(일반)/폴더명/PDF 경로에 자동 저장
            if request.generalName and request.folderTitle:
                safe_general_name = sanitize_filename(request.generalName, "견적서")
                safe_folder_title = sanitize_filename(request.folderTitle, "폴더")
                save_dir = Path(base_path) / safe_general_name / safe_folder_title / "PDF"
                # 폴더가 없으면 생성 (이미 존재하면 skip)
                save_dir.mkdir(parents=True, exist_ok=True)
            else:
                # 폴더 정보가 없으면 기존 방식대로 저장
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


@handler.get("/folder/{folder_id}")
async def export_folder_pdf(folder_id: UUID, db: Session = Depends(get_db)):
    """
    폴더의 모든 견적서를 하나의 PDF 파일로 통합 다운로드
    순서: 갑지(Header), 을지(Detailed), 내정가비교서(PriceCompare)
    각 문서는 PyPDF2를 사용하여 병합됨
    """
    try:
        # 1. 폴더 정보 가져오기
        from backend.api.v1.quotation.folder.crud import (
            get_folder_by_id,
            get_folder_resources,
        )

        folder = get_folder_by_id(db, folder_id)
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")

        # 2. 폴더의 각 리소스 조회
        resources = get_folder_resources(db, folder_id)

        header_resource = next(
            (r for r in resources if r["table_name"] == "견적서"), None
        )
        detailed_resource = next(
            (r for r in resources if r["table_name"] == "견적서(을지)"), None
        )
        price_compare_resource = next(
            (r for r in resources if r["table_name"] == "내정가 비교"), None
        )

        # 3. PyPDF2를 사용하여 PDF 병합
        from PyPDF2 import PdfMerger

        merger = PdfMerger()

        # 4. 각 문서의 PDF 생성 및 병합 (순서: 갑지, 을지, 내정가비교서)
        base_url = "http://localhost:8000"  # 실제 서버 URL로 변경 필요

        # 4-1. 갑지 PDF
        if header_resource:
            try:
                header_url = f"{base_url}/service/quotation/general/header/detail/{header_resource['id']}"
                header_pdf = await generate_pdf_bytes(header_url)
                merger.append(BytesIO(header_pdf))
            except Exception as e:
                print(f"갑지 PDF 생성 오류: {e}")

        # 4-2. 을지 PDF
        if detailed_resource:
            try:
                detailed_url = f"{base_url}/service/quotation/general/detailed/detail/{detailed_resource['id']}"
                detailed_pdf = await generate_pdf_bytes(detailed_url)
                merger.append(BytesIO(detailed_pdf))
            except Exception as e:
                print(f"을지 PDF 생성 오류: {e}")

        # 4-3. 내정가비교서 PDF
        if price_compare_resource:
            try:
                pc_url = f"{base_url}/service/quotation/general/price_compare/detail/{price_compare_resource['id']}"
                pc_pdf = await generate_pdf_bytes(pc_url)
                merger.append(BytesIO(pc_pdf))
            except Exception as e:
                print(f"내정가비교서 PDF 생성 오류: {e}")

        # 5. 병합된 PDF 저장
        output = BytesIO()
        merger.write(output)
        merger.close()
        output.seek(0)

        # 6. 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{folder.title}_통합견적서_{timestamp}.pdf"

        # 7. StreamingResponse로 반환
        return StreamingResponse(
            output,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Folder PDF export error: {str(e)}"
        )
