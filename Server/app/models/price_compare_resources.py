# app/models/price_compare_resources.py
from sqlalchemy import Column, String, Integer, Text, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class PriceCompareResources(Base):
    __tablename__ = "price_compare_resources"
    
    # 1. PK: 어떤 견적 비교서인지
    price_compare_id = Column(UUID(as_uuid=True), primary_key=True) 
    
    # 2. PK [추가]: 어떤 장비의 자원인지 (이게 있어야 장비별 구분이 됨) 💡
    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    major = Column(String(30), primary_key=True)
    minor = Column(String(50), primary_key=True)
    
    # Data Columns
    cost_solo_price = Column(Integer, nullable=False)
    cost_unit = Column(String(10), nullable=False)
    cost_compare = Column(Integer, nullable=False)
    quotation_solo_price = Column(Integer, nullable=False)
    quotation_unit = Column(String(10), nullable=False)
    quotation_compare = Column(Integer, nullable=False)
    upper = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    price_compare = relationship("PriceCompare", back_populates="price_compare_resources")
    
    # 복합 FK 제약 조건
    __table_args__ = (
        # Price Compare 연결
        ForeignKeyConstraint(
            ['price_compare_id'],
            ['price_compare.id'],
            ondelete='CASCADE'
        ),
        # Machine 연결 (장비 삭제 시 해당 리소스도 삭제되도록) 💡
        ForeignKeyConstraint(
            ['machine_id'],
            ['machine.id'],
            ondelete='CASCADE'
        ),
    )

    def __repr__(self):
        return f"<PriceCompareResources(pc_id='{self.price_compare_id}', machine_id='{self.machine_id}', major='{self.major}')>"