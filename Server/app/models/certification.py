# app/models/certification.py
#
# 부품(Resources)의 인증 정보를 정의하는 SQLAlchemy 모델입니다.
# - 각 부품이 획득한 UL, CE, KC 등의 인증 여부와 기타 특이사항을 기록합니다.
#

from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKeyConstraint, TIMESTAMP # 컬럼 타입 임포트
from sqlalchemy.sql import func # SQL 함수 임포트
from sqlalchemy.orm import relationship # 관계 정의를 위함
from database import Base # SQLAlchemy 모델의 베이스 클래스 임포트

class Certification(Base):
    """
    'certification' 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    부품(Resources)의 인증 정보를 저장합니다.
    """
    __tablename__ = "certification" # 매핑될 데이터베이스 테이블 이름
    
    # --- 테이블 컬럼 정의 ---
    id = Column(Integer, primary_key=True, autoincrement=True) # 고유 ID (자동 증가 Primary Key)
    
    # --- 복합 외래 키 정의 ---
    # Resources 테이블의 복합 Primary Key를 참조합니다.
    resources_id = Column(String(6), nullable=False, index=True) # 자재 ID (Resources.id 참조)
    maker_id = Column(String(4), nullable=False, index=True) # 제조사 ID (Resources.maker_id 참조)
    
    # --- 인증 정보 필드 ---
    ul = Column(Boolean, nullable=False, default=False) # UL 인증 여부 (True/False)
    ce = Column(Boolean, nullable=False, default=False) # CE 인증 여부
    kc = Column(Boolean, nullable=False, default=False) # KC 인증 여부
    etc = Column(Text, nullable=True) # 기타 인증 또는 비고 사항 (자유 형식 텍스트)

    # 타임스탬프 필드
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp()) # 생성일시
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()) # 수정일시
    
    # --- 관계 정의 ---
    # Certification과 Resources 간의 1:1 관계 (Certification은 하나의 Resource에 속함)
    resource = relationship(
        "Resources",
        back_populates="certification",
        foreign_keys=[resources_id, maker_id], # 복합 외래 키 지정
        primaryjoin="and_(Certification.resources_id==Resources.id, Certification.maker_id==Resources.maker_id)"
    )
    
    # --- 복합 외래 키 제약조건 ---
    # resources 테이블의 (maker_id, id) 복합 키를 외래 키로 참조합니다.
    __table_args__ = (
        ForeignKeyConstraint(
            ['resources_id', 'maker_id'], # Certification 테이블의 컬럼
            ['resources.id', 'resources.maker_id'] # Resources 테이블의 컬럼
        ),
    )
    
    def __repr__(self):
        """객체를 문자열로 표현할 때 사용됩니다."""
        return f"<Certification(id={self.id}, resources_id='{self.resources_id}', maker_id='{self.maker_id}')>"
