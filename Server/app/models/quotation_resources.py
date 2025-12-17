# app/models/quotation_resources.py

from sqlalchemy import Column, String, Integer, Text, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from database import Base
from db_types import UUID

class QuotationResources(Base):
    __tablename__ = "quotation_resources"
    
    # PK, FK to quotation
    quotation_id = Column(UUID, primary_key=True) 
    
    # PK
    name = Column(String(100), primary_key=True)
    
    # Data Columns
    spac = Column(String(50), nullable=True)
    compare = Column(Integer, nullable=False)
    unit = Column(String(10), nullable=False)
    solo_price = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    quotation = relationship("Quotation", back_populates="quotation_resources")

    # 복합 FK 제약 조건
    __table_args__ = (
        ForeignKeyConstraint(
            ['quotation_id'],
            ['quotation.id'],
            ondelete='CASCADE'
        ),
    )
    
    def __repr__(self):
        return f"<QuotationResources(quotation_id='{self.quotation_id}', name='{self.name}')>"