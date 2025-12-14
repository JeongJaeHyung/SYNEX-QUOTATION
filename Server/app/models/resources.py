# app/models/resources.py
#
# 시스템에 등록된 모든 부품/자재의 마스터 데이터를 정의하는 SQLAlchemy 모델입니다.
# - 제조사별 고유 ID를 가지며, 대분류, 중분류, 모델명, 단가 등의 정보를 포함합니다.
# - 견적서 구성의 기본 단위가 됩니다.
#

from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP # 컬럼 타입 임포트
from sqlalchemy.sql import func # SQL 함수 임포트
from sqlalchemy.orm import relationship # 관계 정의를 위함
from database import Base # SQLAlchemy 모델의 베이스 클래스 임포트

class Resources(Base):
    """
    'resources' 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    부품 및 자재의 마스터 데이터(상품 카탈로그)를 저장합니다.
    """
    __tablename__ = "resources" # 매핑될 데이터베이스 테이블 이름
    
    # --- 복합 Primary Key 정의 ---
    # 부품 ID와 제조사 ID를 함께 사용하여 각 부품을 고유하게 식별합니다.
    id = Column(String(6), primary_key=True, index=True) # 자재 ID (6자리 고유 코드)
    maker_id = Column(String(4), ForeignKey("maker.id"), primary_key=True, index=True) # 제조사 ID (외래 키, Maker 테이블의 id 참조)
    
    # --- 기본 컬럼 정의 ---
    major = Column(String(50), nullable=False) # 대분류 (Unit, 예: '판넬', '인건비')
    minor = Column(String(50), nullable=False) # 중분류 (품목, 예: '차단기', 'PLC Set', '조립')
    name = Column(String(100), nullable=False) # 모델명/규격 (예: 'FX5U-32MT/ES', '해체 및 포장')
    unit = Column(String(10), nullable=False) # 단위 (예: 'ea', 'M/D', 'set')
    solo_price = Column(Integer, nullable=False) # 개별 부품의 기본 단가
    display_order = Column(Integer, nullable=False) # 목록에 표시될 순서

    # 타임스탬프 필드
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp()) # 생성일시
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()) # 수정일시
    
    # --- 관계 정의 ---
    # Resources와 Maker 간의 N:1 관계 (Resources는 하나의 Maker에 속함)
    maker = relationship("Maker", back_populates="resources")
    # Resources와 Certification 간의 1:1 관계 (하나의 Resource는 하나의 Certification 정보를 가짐)
    certification = relationship("Certification", back_populates="resource", uselist=False)
    
    def __repr__(self):
        """객체를 문자열로 표현할 때 사용됩니다."""
        return f"<Resources(id='{self.id}', maker_id='{self.maker_id}', name='{self.name}')>"