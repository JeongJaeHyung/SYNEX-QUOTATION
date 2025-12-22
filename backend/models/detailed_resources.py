# app/models/detailed_resources.py

from sqlalchemy import Column, String, Integer, Text, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base

class DetailedResources(Base):
    __tablename__ = "detailed_resources"
    
    # PK, FK to detailed
    detailed_id = Column(UUID(as_uuid=True), primary_key=True)
    # machine_name은 FK가 아니라 "스냅샷" 용도로 저장하는 필드입니다.
    # (예: 상세정보 생성 시점의 장비/머신명을 저장) 따라서 FK 제약을 걸지 않습니다.
    machine_name = Column(String(100), primary_key=True, comment="snapshot: not a FK")
    
    # PK
    major = Column(String(30), primary_key=True)
    minor = Column(String(50), primary_key=True)
    
    # Data Columns
    unit = Column(String(10), nullable=False)
    solo_price = Column(Integer, nullable=False)
    compare = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    detailed = relationship("Detailed", back_populates="detailed_resources")
    
    # 복합 FK 제약 조건: detailed_id만 Detailed.id를 참조합니다 (machine_name은 참조하지 않음)
    __table_args__ = (
        ForeignKeyConstraint(
            ['detailed_id'],
            ['detailed.id'],
            ondelete='CASCADE'
        ),
    )

    def __repr__(self):
        return f"<DetailedResources(detailed_id='{self.detailed_id}', major='{self.major}', minor='{self.minor}')>"