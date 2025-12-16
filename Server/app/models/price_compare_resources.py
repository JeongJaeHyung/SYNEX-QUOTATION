# app/models/price_compare_resources.py
from sqlalchemy import Column, String, Integer, Text, ForeignKeyConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class PriceCompareResources(Base):
    __tablename__ = "price_compare_resources"
    
    # PK, FK to price_compare
    price_compare_id = Column(UUID(as_uuid=True), ForeignKey("price_compare.id", ondelete="CASCADE"), primary_key=True) 
    
    # PK
    major = Column(String(30), primary_key=True)
    minor = Column(String(50), primary_key=True)
    # 중복 uuid 컬럼 제거
    
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
        ForeignKeyConstraint(
            ['price_compare_id'],
            ['price_compare.id'],
            ondelete='CASCADE'
        ),
    )

    def __repr__(self):
        return f"<PriceCompareResources(pc_id='{self.price_compare_id}', major='{self.major}', minor='{self.minor}')>"