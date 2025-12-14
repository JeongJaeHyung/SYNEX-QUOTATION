# api/v1/account/crud.py
#
# 사용자 계정(Account) 데이터베이스 작업을 위한 CRUD(Create, Read, Update, Delete) 함수를 정의합니다.
# - 계정 생성, 조회, 중복 확인 및 비밀번호 검증 로직을 포함합니다.
# - 비밀번호는 bcrypt를 사용하여 안전하게 해싱 처리합니다.
#

from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위함
from sqlalchemy import or_ # SQLAlchemy OR 조건 사용을 위함
from typing import Optional # 타입 힌트 (선택적 인자)
from models.account import Account # Account 모델 임포트
import bcrypt # 비밀번호 해싱 라이브러리

# ============================================================
# Account CRUD 함수
# ============================================================

def create_account(
    db: Session,
    id: str,
    pwd: str, # 프론트엔드에서 1차 해싱된 비밀번호
    name: str,
    department: str,
    position: str,
    phone_number: str,
    e_mail: str
) -> Account:
    """
    새로운 사용자 계정을 생성하고 데이터베이스에 저장합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        id (str): 사용자 계정 ID.
        pwd (str): 프론트엔드에서 1차 해싱된 비밀번호.
        name (str): 사용자 이름.
        department (str): 사용자 부서.
        position (str): 사용자 직급.
        phone_number (str): 사용자 전화번호.
        e_mail (str): 사용자 이메일.
        
    Returns:
        Account: 생성된 Account 객체.
    """
    # 백엔드 재해싱 (이중 해싱)
    # 프론트에서 받은 해시된 비밀번호를 다시 해싱하여 보안을 강화합니다.
    salt = bcrypt.gensalt() # 비밀번호마다 고유한 salt 생성
    final_hash = bcrypt.hashpw(pwd.encode('utf-8'), salt) # 비밀번호 해싱
    
    # Account 모델 인스턴스 생성
    account = Account(
        id=id,
        pwd=final_hash.decode('utf-8'),  # 최종 해시된 비밀번호를 문자열로 저장
        name=name,
        department=department,
        position=position,
        phone_number=phone_number,
        e_mail=e_mail
    )
    
    db.add(account)    # 세션에 Account 객체 추가
    db.commit()        # 트랜잭션 커밋 (DB에 변경사항 반영)
    db.refresh(account) # 커밋된 Account 객체를 최신 상태로 새로고침
    return account


def get_account_by_id(db: Session, account_id: str) -> Optional[Account]:
    """
    Account ID를 사용하여 데이터베이스에서 계정 정보를 조회합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        account_id (str): 조회할 계정 ID.
        
    Returns:
        Optional[Account]: 조회된 Account 객체, 없으면 None.
    """
    return db.query(Account).filter(Account.id == account_id).first()


def get_account_by_email(db: Session, email: str) -> Optional[Account]:
    """
    Account 이메일을 사용하여 데이터베이스에서 계정 정보를 조회합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        email (str): 조회할 계정 이메일.
        
    Returns:
        Optional[Account]: 조회된 Account 객체, 없으면 None.
    """
    return db.query(Account).filter(Account.e_mail == email).first()


def get_account_by_phone(db: Session, phone_number: str) -> Optional[Account]:
    """
    Account 전화번호를 사용하여 데이터베이스에서 계정 정보를 조회합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        phone_number (str): 조회할 계정 전화번호.
        
    Returns:
        Optional[Account]: 조회된 Account 객체, 없으면 None.
    """
    return db.query(Account).filter(Account.phone_number == phone_number).first()


def check_account_exists(
    db: Session,
    id: Optional[str] = None,
    pwd: Optional[str] = None, # 중복 체크에서는 사용 안 함
    name: Optional[str] = None, # 중복 체크에서는 사용 안 함
    department: Optional[str] = None, # 중복 체크에서는 사용 안 함
    position: Optional[str] = None, # 중복 체크에서는 사용 안 함
    phone_number: Optional[str] = None,
    e_mail: Optional[str] = None
) -> bool:
    """
    주어진 조건(ID, 이메일, 전화번호)으로 계정의 존재 여부를 확인합니다.
    주로 회원가입 시 아이디/이메일/전화번호 중복 확인에 사용됩니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        id (Optional[str]): 확인할 계정 ID.
        phone_number (Optional[str]): 확인할 전화번호.
        e_mail (Optional[str]): 확인할 이메일.
        
    Returns:
        bool: 조건 중 하나라도 일치하는 계정이 존재하면 True, 모두 일치하지 않으면 False.
    """
    query = db.query(Account)
    
    conditions = [] # OR 조건들을 담을 리스트
    
    # ID, 이메일, 전화번호 필드에 대해 중복 조건을 추가합니다.
    if id:
        conditions.append(Account.id == id)
    if e_mail:
        conditions.append(Account.e_mail == e_mail)
    if phone_number:
        conditions.append(Account.phone_number == phone_number)
    
    # 비밀번호, 이름, 부서, 직급은 중복 체크의 대상이 아니므로 사용하지 않습니다.
    
    if not conditions:
        return False # 중복 체크 조건이 없으면 항상 False 반환
    
    # OR 조건으로 필터링하여 첫 번째 일치하는 레코드를 찾습니다.
    result = query.filter(or_(*conditions)).first()
    return result is not None # 레코드가 존재하면 True, 없으면 False


def verify_login(
    db: Session,
    id: str,
    pwd: str # 프론트엔드에서 1차 해싱된 비밀번호
) -> Optional[Account]:
    """
    로그인 정보를 검증합니다. 주어진 ID와 비밀번호가 일치하는 계정을 찾습니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        id (str): 로그인 시도 계정 ID.
        pwd (str): 프론트엔드에서 1차 해싱된 비밀번호.
        
    Returns:
        Optional[Account]: 로그인 성공 시 Account 객체, 실패 시 None.
    """
    account = get_account_by_id(db, id) # ID로 계정 조회
    if not account:
        return None # 계정이 존재하지 않음
    
    # 비밀번호 검증
    # 프론트엔드에서 1차 해싱된 비밀번호(pwd)와 DB에 저장된 2차 해싱된 비밀번호(account.pwd)를 비교합니다.
    if bcrypt.checkpw(pwd.encode('utf-8'), account.pwd.encode('utf-8')):
        return account # 비밀번호 일치, Account 객체 반환
    
    return None # 비밀번호 불일치
