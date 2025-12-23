# app/models/quotation_resources.py

from sqlalchemy import Column, String, Integer, Text, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base

class HeaderResources(Base):
    __tablename__ = "header_resources"
    
    # PK, FK to header
    header_id = Column(UUID(as_uuid=True), primary_key=True) 
    
    # PK
    machine = Column(String(100), primary_key=True)
    
    name = Column(String(100), primary_key=True)
    
    # Data Columns
    spac = Column(String(50), nullable=True)
    compare = Column(Integer, nullable=False)
    unit = Column(String(10), nullable=False)
    solo_price = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    header = relationship("Header", back_populates="header_resources")

    # 복합 FK 제약 조건
    __table_args__ = (
        ForeignKeyConstraint(
            ['header_id'],
            ['header.id'],
            ondelete='CASCADE'
        ),
    )
    
    def __repr__(self):
        return f"<HeaderResources(header_id='{self.header_id}', name='{self.name}')>"