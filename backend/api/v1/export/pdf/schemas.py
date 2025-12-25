# backend/api/v1/download/schemas.py
from pydantic import BaseModel


class SettingsModel(BaseModel):
    """PDF 저장 설정"""
    pdfSavePath: str = ""
    askSaveLocation: bool = False


class PDFSaveRequest(BaseModel):
    """PDF 저장 요청"""
    url: str
    filename: str
    projectName: str = ""
    docType: str = ""


class PDFSaveResponse(BaseModel):
    """PDF 저장 응답"""
    success: bool
    path: str = ""
    message: str = ""


class FolderSelectResponse(BaseModel):
    """폴더 선택 응답"""
    success: bool
    path: str = ""