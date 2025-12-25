# backend/api/v1/export/excel/handler.py
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from pathlib import Path

from backend.database import get_db
from . import crud
from .Format import header, detailed, price_compare

# PDF 모듈의 로직 재활용
from ..pdf.crud import (
    load_settings,
    get_save_file_path,
    open_file_in_explorer,
    sanitize_filename
)

handler = APIRouter()

@handler.get("/{quotation_type}/{quotation_id}")
async def export_excel(
    quotation_type: str,
    quotation_id: UUID,
    db: Session = Depends(get_db)
):
    """
    견적서 Excel 내보내기 (PDF 저장 설정 및 로직 적용)
    """
    # 1. quotation_type 검증
    valid_types = ["header", "detailed", "price_compare"]
    if quotation_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid quotation_type. Must be one of {valid_types}"
        )
    
    # 2. 데이터 조회
    try:
        if quotation_type == "header":
            data = crud.get_header_data(db, quotation_id)
            type_name = "갑지"
        elif quotation_type == "detailed":
            data = crud.get_detailed_data(db, quotation_id)
            type_name = "을지"
        elif quotation_type == "price_compare":
            data = crud.get_price_compare_data(db, quotation_id)
            type_name = "내역"
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # 3. Excel 파일 생성 (바이너리)
    try:
        if quotation_type == "header":
            excel_file = header.create_excel(data)
        elif quotation_type == "detailed":
            excel_file = detailed.create_excel(data)
        elif quotation_type == "price_compare":
            excel_file = price_compare.create_excel(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel generation error: {str(e)}")
    
    # 4. 저장 경로 및 파일명 결정 (PDF 로직 적용)
    try:
        settings = load_settings()
        base_path = settings.get("pdfSavePath") or str(Path.home() / "Documents" / "JLT_견적서")
        ask_location = settings.get("askSaveLocation", False)

        # 파일명 생성 및 안전한 이름 변환
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        raw_filename = f"견적서({type_name})_{timestamp}.xlsx"
        safe_filename = sanitize_filename(raw_filename)
        safe_doctype = sanitize_filename(type_name, '문서')

        if ask_location:
            # 💡 Windows 대화상자 사용 (Executor로 비동기 처리)
            loop = asyncio.get_event_loop()
            file_path = await loop.run_in_executor(
                None,
                lambda: get_save_file_path(safe_filename, base_path) # PDF crud의 함수 재활용
            )

            if not file_path:
                return JSONResponse({"success": False, "message": "저장이 취소되었습니다."})
            
            # 확장자가 없으면 자동으로 붙여줌
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'
        else:
            # 💡 설정된 경로에 자동 저장
            save_dir = Path(base_path) / safe_doctype
            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = str(save_dir / safe_filename)

        # 5. 파일 물리적 저장
        with open(file_path, "wb") as f:
            f.write(excel_file.getvalue())

        # 6. 탐색기 열기 (위치 질문이 아닐 때만)
        if not ask_location:
            open_file_in_explorer(file_path)

        # 7. 응답 반환 (JSON)
        return JSONResponse({
            "success": True, 
            "path": file_path,
            "message": "성공적으로 저장되었습니다."
        })

    except Exception as e:
        return JSONResponse({"success": False, "message": f"File save error: {str(e)}"})