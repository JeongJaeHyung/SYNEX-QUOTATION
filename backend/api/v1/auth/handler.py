from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core import security
from backend.database import get_db
from backend.models.account import Account

from .schemas import LoginRequest, Token

# [중요] 로그인은 보안 검사를 받으면 안 되므로 일반 APIRouter 사용
handler = APIRouter()


@handler.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # 1. 사용자 조회
    user = db.query(Account).filter(Account.id == login_data.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 일치하지 않습니다.",
        )

    # 2. 비밀번호 검증 (security.py 사용)
    if not security.verify_password(login_data.pwd, user.pwd):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 일치하지 않습니다.",
        )

    # 3. 토큰 발급
    access_token = security.create_access_token(subject=user.id)

    # 4. Role 이름 가져오기 (없으면 GUEST)
    role_name = user.role.name if user.role else "GUEST"

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_name": user.name,
        "role": role_name,
    }
