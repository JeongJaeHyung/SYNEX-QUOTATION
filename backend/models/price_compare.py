#app/models/price_compare.py

from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base

class PriceCompare(Base):
    __tablename__ = "price_compare"
    
    # ID (Primary Key, UUID)만 사용, 중복 uuid 컬럼 제거
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FK to general
    general_id = Column(UUID(as_uuid=True), ForeignKey("general.id", ondelete="CASCADE"), nullable=False)
    
    creator = Column(String(25), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    description = Column(Text, nullable=True)
    
    # Relationships
    general = relationship("General", back_populates="price_compares")
    price_compare_resources = relationship("PriceCompareResources", back_populates="price_compare", cascade="all, delete-orphan")
    price_compare_machines = relationship("PriceCompareMachine", back_populates="price_compare", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<PriceCompare(id='{self.id}', general_id='{self.general_id}')>"