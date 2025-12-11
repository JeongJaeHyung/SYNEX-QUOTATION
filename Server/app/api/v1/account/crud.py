# api/v1/account/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from models.account import Account
import bcrypt

# ============================================================
# Account CRUD
# ============================================================

def create_account(
    db: Session,
    id: str,
    pwd: str,
    name: str,
    department: str,
    position: str,
    phone_number: str,
    e_mail: str
) -> Account:
    """
    Account 생성
    
    - pwd는 프론트엔드에서 해시된 값을 받음
    - 백엔드에서 재해싱 (이중 해싱)
    """
    # 백엔드 재해싱 (이중 해싱)
    salt = bcrypt.gensalt()
    final_hash = bcrypt.hashpw(pwd.encode('utf-8'), salt)
    
    account = Account(
        id=id,
        pwd=final_hash.decode('utf-8'),  # 최종 해시 저장
        name=name,
        department=department,
        position=position,
        phone_number=phone_number,
        e_mail=e_mail
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account_by_id(db: Session, account_id: str) -> Optional[Account]:
    """Account ID로 조회"""
    return db.query(Account).filter(Account.id == account_id).first()


def get_account_by_email(db: Session, email: str) -> Optional[Account]:
    """Account Email로 조회"""
    return db.query(Account).filter(Account.e_mail == email).first()


def get_account_by_phone(db: Session, phone_number: str) -> Optional[Account]:
    """Account 전화번호로 조회"""
    return db.query(Account).filter(Account.phone_number == phone_number).first()


def check_account_exists(
    db: Session,
    id: Optional[str] = None,
    pwd: Optional[str] = None,
    name: Optional[str] = None,
    department: Optional[str] = None,
    position: Optional[str] = None,
    phone_number: Optional[str] = None,
    e_mail: Optional[str] = None
) -> bool:
    """
    Account 중복 체크
    
    - 하나라도 일치하면 True (사용 불가)
    - 모두 일치하지 않으면 False (사용 가능)
    """
    query = db.query(Account)
    
    conditions = []
    
    if id:
        conditions.append(Account.id == id)
    if e_mail:
        conditions.append(Account.e_mail == e_mail)
    if phone_number:
        conditions.append(Account.phone_number == phone_number)
    
    # pwd, name, department, position은 중복 체크에 사용 안 함
    # (로그인 용도이거나 중복 체크 의미 없음)
    
    if not conditions:
        return False
    
    # OR 조건으로 하나라도 일치하면 True
    result = query.filter(or_(*conditions)).first()
    return result is not None


def verify_login(
    db: Session,
    id: str,
    pwd: str
) -> Optional[Account]:
    """
    로그인 검증
    
    - id로 계정 찾기
    - 비밀번호 검증 (이중 해싱 비교)
    """
    account = get_account_by_id(db, id)
    if not account:
        return None
    
    # 비밀번호 검증
    # pwd는 프론트엔드 해시 (1차)
    # account.pwd는 백엔드 해시 (2차)
    if bcrypt.checkpw(pwd.encode('utf-8'), account.pwd.encode('utf-8')):
        return account
    
    return None