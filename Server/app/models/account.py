# app/models/account.py
#
# 사용자 계정 정보를 정의하는 SQLAlchemy 모델입니다.
# - 계정 아이디, 비밀번호, 이름, 부서, 직급, 전화번호, 이메일 등의 필드를 포함합니다.
# - 계정 관리에 사용됩니다.
#

from sqlalchemy import Column, String, TIMESTAMP # 컬럼 타입 임포트
from sqlalchemy.sql import func # SQL 함수 (예: current_timestamp) 임포트
from database import Base # SQLAlchemy 모델의 베이스 클래스 임포트

class Account(Base):
    """
    'account' 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    시스템 사용자의 계정 정보를 저장합니다.
    """
    __tablename__ = "account" # 매핑될 데이터베이스 테이블 이름

    # --- 테이블 컬럼 정의 ---
    # 필드명 통일 규칙: 계정 아이디(id), 비밀번호(pwd)
    id = Column(String(25), primary_key=True, index=True) # 계정 ID (Primary Key, 인덱스 생성)
    pwd = Column(String(255), nullable=False) # 비밀번호 (암호화된 문자열 저장)
    name = Column(String(10), nullable=False) # 사용자 이름
    department = Column(String(25), nullable=False) # 부서
    position = Column(String(25), nullable=False) # 직급
    phone_number = Column(String(11), nullable=False) # 전화번호 (하이픈 없이 숫자만)
    e_mail = Column(String(255), nullable=False, unique=True) # 이메일 (필수, 고유 값)

    # 타임스탬프 필드
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp()) # 생성일시 (레코드 생성 시 자동 기록)
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()) # 수정일시 (레코드 업데이트 시 자동 기록)

    def __repr__(self):
        """객체를 문자열로 표현할 때 사용됩니다."""
        return f"<Account(id='{self.id}', name='{self.name}', department='{self.department}')>"
