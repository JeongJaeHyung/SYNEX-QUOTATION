from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

# ============================================================
# Account Schemas
# ============================================================

class AccountRegister(BaseModel):
    """Account 등록 요청"""
    id: str = Field(..., min_length=3, max_length=25)
    pwd: str = Field(..., min_length=8, max_length=255)
    name: str = Field(..., max_length=10)
    department: str = Field(..., max_length=25)
    position: str = Field(..., max_length=25)
    phone_number: str = Field(..., pattern=r'^\d{10,11}$', max_length=11)
    e_mail: EmailStr

class AccountCheck(BaseModel):
    """
    Account 중복 조회 요청 (선택적)
    - 로그인 기능이 Auth API로 이관되었으므로 pwd 필드 제거함
    """
    id: Optional[str] = Field(None, max_length=25)
    # pwd: Optional[str] = Field(None, max_length=255)  <-- 삭제 (불필요)
    name: Optional[str] = Field(None, max_length=10)
    department: Optional[str] = Field(None, max_length=25)
    position: Optional[str] = Field(None, max_length=25)
    phone_number: Optional[str] = Field(None, max_length=11)
    e_mail: Optional[EmailStr] = None

class AccountRegisterResponse(BaseModel):
    """Account 등록 응답"""
    id: str
    name: str
    department: str
    position: str
    phone_number: str
    e_mail: str
    created_at: datetime
    message: str

class AccountCheckResponse(BaseModel):
    """Account 중복 조회 응답"""
    available: bool
    message: str