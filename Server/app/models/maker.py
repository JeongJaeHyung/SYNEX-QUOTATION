# app/models/maker.py
#
# 제조사 정보를 정의하는 SQLAlchemy 모델입니다.
# - 부품(Resources)을 생산하는 제조사(브랜드)의 ID와 이름을 관리합니다.
#

from sqlalchemy import Column, String, TIMESTAMP # 컬럼 타입 임포트
from sqlalchemy.sql import func # SQL 함수 임포트
from sqlalchemy.orm import relationship # 관계(Relationship) 정의를 위함
from database import Base # SQLAlchemy 모델의 베이스 클래스 임포트

class Maker(Base):
    """
    'maker' 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    부품의 제조사(브랜드) 정보를 저장합니다.
    """
    __tablename__ = "maker" # 매핑될 데이터베이스 테이블 이름
    
    # --- 테이블 컬럼 정의 ---
    id = Column(String(4), primary_key=True, index=True) # 제조사 ID (Primary Key, 4자리 고유 코드)
    name = Column(String(100), nullable=False) # 제조사 이름 (예: 'LS ELECTRIC', 'RITTAL')

    # 타임스탬프 필드
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp()) # 생성일시
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()) # 수정일시
    
    # --- 관계 정의 ---
    # Maker와 Resources 간의 1:N 관계 정의
    # 'Resources' 모델에서 'maker' 필드를 통해 이 Maker 객체에 접근할 수 있습니다.
    resources = relationship("Resources", back_populates="maker")
    
    def __repr__(self):
        """객체를 문자열로 표현할 때 사용됩니다."""
        return f"<Maker(id='{self.id}', name='{self.name}')>"
