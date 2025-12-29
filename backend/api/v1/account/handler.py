from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.v1.account import crud, schemas
from backend.database import get_db

# [중요] 회원가입/중복체크는 로그인 없이 가능해야 하므로 RBACRoute 적용 안 함 (또는 Whitelist 등록)
handler = APIRouter()


@handler.post(
    "/register", response_model=schemas.AccountRegisterResponse, status_code=201
)
def register_account(account: schemas.AccountRegister, db: Session = Depends(get_db)):
    """Account 등록"""
    # 중복 체크
    if crud.get_account_by_id(db, account.id):
        raise HTTPException(status_code=409, detail="이미 사용 중인 아이디입니다.")
    if crud.get_account_by_email(db, account.e_mail):
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
    if crud.get_account_by_phone(db, account.phone_number):
        raise HTTPException(status_code=409, detail="이미 사용 중인 전화번호입니다.")

    # 생성
    db_account = crud.create_account(
        db=db,
        id=account.id,
        pwd=account.pwd,
        name=account.name,
        department=account.department,
        position=account.position,
        phone_number=account.phone_number,
        e_mail=account.e_mail,
    )

    return {
        "id": db_account.id,
        "name": db_account.name,
        "department": db_account.department,
        "position": db_account.position,
        "phone_number": db_account.phone_number,
        "e_mail": db_account.e_mail,
        "created_at": db_account.created_at,
        "message": "성공적으로 계정이 생성되었습니다.",
    }


@handler.post("/check", response_model=schemas.AccountCheckResponse)
def check_account(check_data: schemas.AccountCheck, db: Session = Depends(get_db)):
    """
    Account 중복 조회 (로그인 기능 제거됨)
    - available: true (사용 가능)
    - available: false (이미 사용 중)
    """
    # 최소 1개 필드 확인
    if not any([check_data.id, check_data.e_mail, check_data.phone_number]):
        raise HTTPException(
            status_code=422, detail="중복 확인할 필드(id, email, phone)가 필요합니다."
        )

    # 중복 체크
    exists = crud.check_account_exists(
        db=db,
        id=check_data.id,
        e_mail=check_data.e_mail,
        phone_number=check_data.phone_number,
    )

    if exists:
        return {"available": False, "message": "이미 등록된 정보입니다."}
    else:
        return {"available": True, "message": "사용 가능한 정보입니다."}
