# app/models/machine.py
#
# 견적서(또는 장비 템플릿)의 메인 정보를 정의하는 SQLAlchemy 모델입니다.
# - 장비명, 고객사, 작성자, 총 금액, 비고 등의 필드를 포함합니다.
# - 견적의 상위 개념 역할을 합니다.
#

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP # 컬럼 타입 임포트
from sqlalchemy.dialects.postgresql import UUID # PostgreSQL UUID 타입 사용을 위함
from sqlalchemy.sql import func # SQL 함수 임포트
from sqlalchemy.orm import relationship # 관계 정의를 위함
import uuid # UUID 기본값 생성을 위함
from database import Base # SQLAlchemy 모델의 베이스 클래스 임포트

class Machine(Base):
    """
    'machine' 테이블과 매핑되는 SQLAlchemy ORM 모델입니다.
    하나의 견적서 또는 장비 템플릿의 기본 정보를 저장합니다.
    """
    __tablename__ = "machine" # 매핑될 데이터베이스 테이블 이름
    
    # --- 테이블 컬럼 정의 ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # 장비/견적서 ID (Primary Key, UUID 타입 자동 생성)
    name = Column(String(100), nullable=False) # 장비명 또는 견적명
    manufacturer = Column(String(50), nullable=True)  # 장비 제조사 (견적서에 기록되는 정보)
    client = Column(String(50), nullable=True)         # 고객사명 (견적서에 기록되는 정보)
    creator = Column(String(25), nullable=False)       # 견적서 작성자 (ACCOUNT.name 등과 연결 가능)
    price = Column(Integer, nullable=True)             # 이 견적서의 총 가격
    description = Column(Text, nullable=True)          # 견적서 비고 (자유 형식 텍스트)

    # 타임스탬프 필드
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp()) # 생성일시
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp()) # 수정일시
    
    # --- 관계 정의 ---
    # Machine과 MachineResources 간의 1:N 관계 정의
    # cascade="all, delete-orphan": Machine이 삭제되면 관련된 모든 MachineResources도 함께 삭제됩니다.
    machine_resources = relationship("MachineResources", back_populates="machine", cascade="all, delete-orphan")
    
    def __repr__(self):
        """객체를 문자열로 표현할 때 사용됩니다."""
        return f"<Machine(id='{self.id}', name='{self.name}')>"
