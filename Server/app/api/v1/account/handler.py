# api/v1/account/handler.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from api.v1.account import schemas, crud

handler = APIRouter()

# ============================================================
# Account Endpoints
# ============================================================

@handler.post("/register", response_model=schemas.AccountRegisterResponse, status_code=201)
def register_account(
    account: schemas.AccountRegister,
    db: Session = Depends(get_db)
):
    """
    Account 등록
    
    - id: 아이디 (3~25자)
    - pwd: 비밀번호 (프론트엔드 해시, 백엔드 재해싱)
    - name: 이름
    - department: 부서
    - position: 직급
    - phone_number: 전화번호 (10~11자리 숫자)
    - e_mail: 이메일
    """
    # 중복 체크 (id, email, phone)
    if crud.get_account_by_id(db, account.id):
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")
    
    if crud.get_account_by_email(db, account.e_mail):
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
    
    if crud.get_account_by_phone(db, account.phone_number):
        raise HTTPException(status_code=409, detail="이미 사용 중인 전화번호입니다.")
    
    # Account 생성
    db_account = crud.create_account(
        db=db,
        id=account.id,
        pwd=account.pwd,  # 프론트엔드 해시 → 백엔드 재해싱
        name=account.name,
        department=account.department,
        position=account.position,
        phone_number=account.phone_number,
        e_mail=account.e_mail
    )
    
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
    check_data: schemas.AccountCheck,
    db: Session = Depends(get_db)
):
    """
    Account 중복 조회 / 로그인
    
    **용도:**
    1. 중복 체크: id, e_mail, phone_number 단일 필드
       - available: true (사용 가능)
       - available: false (이미 사용 중)
    
    2. 로그인: id + pwd 조합
       - available: false (로그인 성공)
       - available: true (로그인 실패)
    
    **최소 1개 이상의 필드 필요**
    """
    # 최소 1개 필드 확인
    if not any([
        check_data.id,
        check_data.pwd,
        check_data.e_mail,
        check_data.phone_number,
        check_data.name,
        check_data.department,
        check_data.position
    ]):
        raise HTTPException(status_code=422, detail="최소 1개 이상의 필드가 필요합니다.")
    
    # 로그인 시도 (id + pwd)
    if check_data.id and check_data.pwd:
        account = crud.verify_login(db, check_data.id, check_data.pwd)
        if account:
            return {
                "available": False,
                "message": "로그인 성공"
            }
        else:
            return {
                "available": True,
                "message": "아이디 또는 비밀번호가 일치하지 않습니다."
            }
    
    # 중복 체크
    exists = crud.check_account_exists(
        db=db,
        id=check_data.id,
        e_mail=check_data.e_mail,
        phone_number=check_data.phone_number
    )
    
    if exists:
        return {
            "available": False,
            "message": "등록된 정보입니다."
        }
    else:
        return {
            "available": True,
            "message": "등록되지 않은 정보입니다."
        }