from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from backend.models.account import Account
from backend.models.role import Role
from backend.core.security import get_password_hash

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
    - 비밀번호는 core.security 모듈을 통해 해싱 (단일 해싱)
    - 기본 Role(USER) 자동 할당
    """
    # 1. 비밀번호 해싱
    hashed_password = get_password_hash(pwd)
    
    # 2. 기본 Role 조회 (USER)
    default_role = db.query(Role).filter(Role.name == "USER").first()
    
    account = Account(
        id=id,
        pwd=hashed_password,
        name=name,
        department=department,
        position=position,
        phone_number=phone_number,
        e_mail=e_mail,
        role_id=default_role.id if default_role else None
    )
    
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


def get_account_by_id(db: Session, account_id: str) -> Optional[Account]:
    return db.query(Account).filter(Account.id == account_id).first()


def get_account_by_email(db: Session, email: str) -> Optional[Account]:
    return db.query(Account).filter(Account.e_mail == email).first()


def get_account_by_phone(db: Session, phone_number: str) -> Optional[Account]:
    return db.query(Account).filter(Account.phone_number == phone_number).first()


def check_account_exists(
    db: Session,
    id: Optional[str] = None,
    e_mail: Optional[str] = None,
    phone_number: Optional[str] = None,
    # 인터페이스 유지를 위한 더미 인자들
    pwd: Optional[str] = None,
    name: Optional[str] = None,
    department: Optional[str] = None,
    position: Optional[str] = None,
) -> bool:
    """
    Account 중복 체크
    """
    query = db.query(Account)
    conditions = []
    
    if id:
        conditions.append(Account.id == id)
    if e_mail:
        conditions.append(Account.e_mail == e_mail)
    if phone_number:
        conditions.append(Account.phone_number == phone_number)
    
    if not conditions:
        return False
    
    result = query.filter(or_(*conditions)).first()
    return result is not None