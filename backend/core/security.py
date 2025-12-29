from datetime import datetime, timedelta
from typing import Any, Optional, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

# bcrypt 설정 (단방향 해싱)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증 (입력받은 평문 vs DB에 저장된 해시)"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """비밀번호 해싱 (회원가입 시 사용)"""
    return pwd_context.hash(password)


def create_access_token(subject: str | Any) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Payload 구성 (sub: 사용자 ID)
    to_encode = {"exp": expire, "sub": str(subject)}

    # 서명 (Signing)
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> str | None:
    """토큰 검증 및 사용자 ID 추출 (RBACRoute에서 사용)"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        return user_id
    except JWTError:
        return None
