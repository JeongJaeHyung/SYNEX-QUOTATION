# api/v1/maker/crud.py
#
# 제조사(Maker) 데이터베이스 작업을 위한 CRUD 함수를 정의합니다.
# - 제조사 ID 자동 생성, 생성, 조회, 검색, 수정, 삭제 기능을 제공합니다.
#

from sqlalchemy.orm import Session # 데이터베이스 세션 관리를 위함
from sqlalchemy import func # SQLAlchemy 함수 (예: max, count) 임포트
from typing import List, Optional, Tuple # 타입 힌트 (선택적 인자, 리스트, 튜플)
from backend.models import Maker # Maker 모델 임포트

# ============================================================
# 헬퍼 함수
# ============================================================

def get_next_maker_id(db: Session) -> str:
    """
    새로운 제조사(Maker) ID를 생성합니다.
    - 형식: M001, M002, M003...
    - 기존 'M'으로 시작하는 ID 중 최대값에 1을 더하여 다음 ID를 생성합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        
    Returns:
        str: 새로 생성된 4자리 제조사 ID (예: "M001").
    """
    # 'M'으로 시작하는 기존 Maker ID 중 최대값을 조회합니다.
    max_id = db.query(func.max(Maker.id)).filter(Maker.id.like('M%')).scalar()
    
    if not max_id:
        return "M001" # 기존 ID가 없으면 "M001" 반환
    
    # 최대 ID의 숫자 부분만 추출하여 1을 더하고, 다시 3자리 숫자로 포맷팅합니다.
    try:
        num = int(max_id[1:]) + 1 # "M001" -> 1 -> 2
        return f"M{num:03d}" # 2 -> "M002"
    except (ValueError, TypeError): # ID가 숫자로 변환 불가능한 경우 (예외 처리)
        return "M001" # 오류 발생 시 기본값 반환


# ============================================================
# CRUD 함수
# ============================================================

def create_maker(
    db: Session,
    name: str, # 제조사 이름
    maker_id: Optional[str] = None # ID가 제공되지 않으면 자동 생성
) -> Maker:
    """
    새로운 제조사(Maker)를 생성하고 데이터베이스에 저장합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        maker_id (Optional[str]): 제조사 ID. 제공되지 않으면 자동으로 생성됩니다.
        name (str): 제조사 이름.
        
    Returns:
        Maker: 생성된 Maker 객체.
    """
    # 제조사 ID가 제공되지 않으면 자동으로 생성합니다.
    if not maker_id:
        maker_id = get_next_maker_id(db)
    
    maker = Maker(id=maker_id, name=name) # Maker 모델 인스턴스 생성
    db.add(maker) # 세션에 객체 추가
    db.commit() # 트랜잭션 커밋
    db.refresh(maker) # 객체 새로고침
    return maker


def get_makers(
    db: Session,
    skip: int = 0, # 조회 시작 지점 (OFFSET)
    limit: int = 100 # 조회할 최대 개수 (LIMIT)
) -> Tuple[int, List[Maker]]:
    """
    데이터베이스에서 모든 제조사(Maker) 목록을 조회합니다.
    페이징 기능을 지원하며, 총 제조사 개수와 목록을 반환합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        
    Returns:
        Tuple[int, List[Maker]]: (총 제조사 개수, 제조사 객체 리스트).
    """
    total = db.query(func.count(Maker.id)).scalar() # 총 제조사 개수 조회
    makers = (
        db.query(Maker)
        .order_by(Maker.created_at.desc()) # 생성일시 기준으로 내림차순 정렬
        .offset(skip) # 지정된 수만큼 건너뛰기
        .limit(limit) # 지정된 수만큼 가져오기
        .all() # 모든 결과 반환
    )
    return total, makers


def get_maker_by_id(db: Session, maker_id: str) -> Optional[Maker]:
    """
    제조사 ID를 사용하여 데이터베이스에서 단일 제조사 정보를 조회합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        maker_id (str): 조회할 제조사 ID.
        
    Returns:
        Optional[Maker]: 조회된 Maker 객체, 없으면 None.
    """
    return db.query(Maker).filter(Maker.id == maker_id).first()


def get_maker_by_name(db: Session, name: str) -> Optional[Maker]:
    """
    제조사 이름을 사용하여 데이터베이스에서 단일 제조사 정보를 조회합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        name (str): 조회할 제조사 이름.
        
    Returns:
        Optional[Maker]: 조회된 Maker 객체, 없으면 None.
    """
    return db.query(Maker).filter(Maker.name == name).first()


def search_makers(
    db: Session,
    query: str, # 검색어
    skip: int = 0,
    limit: int = 100
) -> Tuple[int, List[Maker]]:
    """
    제조사 이름에 대한 검색어를 사용하여 제조사 목록을 조회합니다.
    부분 매칭 및 페이징 기능을 지원합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        query (str): 제조사 이름에서 검색할 문자열.
        skip (int): 건너뛸 레코드 수.
        limit (int): 가져올 레코드 최대 수.
        
    Returns:
        Tuple[int, List[Maker]]: (총 검색 결과 개수, 검색된 Maker 객체 리스트).
    """
    query_obj = db.query(Maker).filter(Maker.name.ilike(f"%{query}%")) # 이름 부분 매칭 (대소문자 구분 없음)
    total = query_obj.count() # 검색 결과 총 개수
    makers = (
        query_obj
        .order_by(Maker.created_at.desc()) # 생성일시 기준으로 내림차순 정렬
        .offset(skip)
        .limit(limit)
        .all()
    )
    return total, makers


def update_maker(
    db: Session,
    maker_id: str,
    name: str # 수정할 제조사 이름
) -> Optional[Maker]:
    """
    기존 제조사 정보를 업데이트합니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        maker_id (str): 업데이트할 제조사 ID.
        name (str): 새로 설정할 제조사 이름.
        
    Returns:
        Optional[Maker]: 업데이트된 Maker 객체, 없으면 None (제조사 ID를 찾지 못한 경우).
    """
    maker = get_maker_by_id(db, maker_id) # ID로 제조사 조회
    if not maker:
        return None # 제조사가 없으면 None 반환
    
    maker.name = name # 제조사 이름 업데이트
    db.commit() # 트랜잭션 커밋
    db.refresh(maker) # 객체 새로고침
    return maker


def delete_maker(db: Session, maker_id: str) -> bool:
    """
    제조사 ID를 사용하여 데이터베이스에서 제조사 정보를 삭제합니다.
    - 관련 자원(Resources)이 있는 경우 외래 키 제약 조건에 따라 삭제가 제한될 수 있습니다.
    
    Args:
        db (Session): SQLAlchemy 데이터베이스 세션.
        maker_id (str): 삭제할 제조사 ID.
        
    Returns:
        bool: 삭제 성공 시 True, 실패 시 False (제조사 ID를 찾지 못한 경우).
    """
    maker = get_maker_by_id(db, maker_id) # ID로 제조사 조회
    if not maker:
        return False # 제조사가 없으면 False 반환
    
    db.delete(maker) # 세션에서 객체 삭제
    db.commit() # 트랜잭션 커밋
    return True
