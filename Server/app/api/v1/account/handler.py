# api/v1/account/handler.py
#
# 사용자 계정(Account) 관련 API 엔드포인트를 정의합니다.
# - 계정 등록(/register), 계정 존재 여부 확인(/check) 등의 API를 제공합니다.
# - 클라이언트로부터 요청을 받아 CRUD 함수를 호출하고 응답을 반환합니다.
#

from fastapi import APIRouter, Depends, HTTPException # FastAPI 라우터, 의존성 주입, HTTP 예외 처리
from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위함
from database import get_db # 데이터베이스 세션 의존성 주입
from api.v1.account import schemas, crud # Account 스키마(DTO) 및 CRUD 함수 임포트

# API 라우터 인스턴스 생성
handler = APIRouter()

# ============================================================
# Account Endpoints (계정 관련 API)
# ============================================================

@handler.post("/register", response_model=schemas.AccountRegisterResponse, status_code=201)
def register_account(
    account: schemas.AccountRegister, # 요청 바디는 AccountRegister 스키마를 따름
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    """
    새로운 사용자 계정을 등록하는 API 엔드포인트입니다.
    - 계정 ID, 이메일, 전화번호의 중복을 확인한 후 계정을 생성합니다.
    - 비밀번호는 프론트엔드에서 1차 해싱된 값을 받아 백엔드에서 다시 해싱(이중 해싱)합니다.
    
    Args:
        account (schemas.AccountRegister): 등록할 계정 정보를 담은 DTO.
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        schemas.AccountRegisterResponse: 등록된 계정 정보와 성공 메시지를 담은 DTO.
        
    Raises:
        HTTPException: ID, 이메일, 전화번호 중 하나라도 중복될 경우 409 Conflict.
    """
    # --- 중복 확인 (ID, 이메일, 전화번호) ---
    # 각 필드별로 이미 사용 중인지 확인하여 중복이면 409 Conflict 에러를 발생시킵니다.
    if crud.get_account_by_id(db, account.id):
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")
    
    if crud.get_account_by_email(db, account.e_mail):
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
    
    if crud.get_account_by_phone(db, account.phone_number):
        raise HTTPException(status_code=409, detail="이미 사용 중인 전화번호입니다.")
    
    # --- Account 생성 ---
    # 중복이 없는 경우, CRUD 함수를 호출하여 계정을 생성합니다.
    db_account = crud.create_account(
        db=db,
        id=account.id,
        pwd=account.pwd,  # 프론트엔드에서 해시된 비밀번호를 전달 (CRUD에서 재해싱)
        name=account.name,
        department=account.department,
        position=account.position,
        phone_number=account.phone_number,
        e_mail=account.e_mail
    )
    
    # 생성된 계정 정보로 응답 DTO를 구성하여 반환합니다.
    return {
        "id": db_account.id,
        "name": db_account.name,
        "department": db_account.department,
        "position": db_account.position,
        "phone_number": db_account.phone_number,
        "e_mail": db_account.e_mail,
        "created_at": db_account.created_at,
        "message": "성공적으로 계정이 생성되었습니다."
    }


@handler.post("/check", response_model=schemas.AccountCheckResponse)
def check_account(
    check_data: schemas.AccountCheck, # 요청 바디는 AccountCheck 스키마를 따름
    db: Session = Depends(get_db) # DB 세션 의존성 주입
):
    """
    계정의 존재 여부를 확인하거나 로그인을 시도하는 API 엔드포인트입니다.
    
    **용도:**
    1.  **중복 체크**: 아이디, 이메일, 전화번호 중 하나를 입력하여 이미 등록된 정보인지 확인합니다.
        *   `available: true` (사용 가능)
        *   `available: false` (이미 사용 중)
    2.  **로그인**: 아이디와 비밀번호 조합으로 로그인을 시도합니다.
        *   `available: false` (로그인 성공)
        *   `available: true` (로그인 실패)
    
    Args:
        check_data (schemas.AccountCheck): 확인 또는 로그인할 계정 정보를 담은 DTO.
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        schemas.AccountCheckResponse: 확인 결과 (available 여부 및 메시지)를 담은 DTO.
        
    Raises:
        HTTPException: 요청 바디에 최소 1개 이상의 필드가 없을 경우 422 Unprocessable Entity.
    """
    # --- 최소 1개 필드 확인 ---
    # check_data 객체에 최소한 하나의 유효한 필드(None이 아닌)가 있는지 확인합니다.
    if not any([
        check_data.id,
        check_data.pwd,
        check_data.e_mail,
        check_data.phone_number,
        check_data.name, # 현재는 중복 체크에 사용 안 하지만, DTO에는 포함될 수 있음
        check_data.department, # 현재는 중복 체크에 사용 안 하지만, DTO에는 포함될 수 있음
        check_data.position # 현재는 중복 체크에 사용 안 하지만, DTO에는 포함될 수 있음
    ]):
        raise HTTPException(status_code=422, detail="최소 1개 이상의 필드가 필요합니다.")
    
    # --- 로그인 시도 (ID + 비밀번호 조합) ---
    # ID와 비밀번호가 모두 제공되면 로그인 검증 로직을 수행합니다.
    if check_data.id and check_data.pwd:
        account = crud.verify_login(db, check_data.id, check_data.pwd)
        if account:
            return {
                "available": False, # 로그인 성공 시 '사용 가능'이 아니라 '등록된 정보'로 해석
                "message": "로그인 성공"
            }
        else:
            return {
                "available": True, # 로그인 실패 시 '사용 가능'으로 해석 (아이디/비번 불일치)
                "message": "아이디 또는 비밀번호가 일치하지 않습니다."
            }
    
    # --- 중복 체크 (ID, 이메일, 전화번호) ---
    # 로그인 시도가 아니면, 제공된 정보로 계정의 존재 여부를 확인합니다.
    exists = crud.check_account_exists(
        db=db,
        id=check_data.id,
        e_mail=check_data.e_mail,
        phone_number=check_data.phone_number
    )
    
    if exists:
        return {
            "available": False, # 이미 존재하면 '사용 불가' (중복)
            "message": "등록된 정보입니다."
        }
    else:
        return {
            "available": True, # 존재하지 않으면 '사용 가능'
            "message": "등록되지 않은 정보입니다."
        }
