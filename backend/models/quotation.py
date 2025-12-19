# app/models/quotation.py

from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base

class Quotation(Base):
    __tablename__ = "quotation"
    
    # ID (Primary Key, UUID)만 사용, 중복 uuid 컬럼 제거
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # FK to general
    general_id = Column(UUID(as_uuid=True), ForeignKey("general.id", ondelete="CASCADE"), nullable=False)
    
    creator = Column(String(25), nullable=False)
    title = Column(String(100), nullable=False)
    price = Column(Integer, nullable=True)
    client = Column(String(50), nullable=True)
    pic_name = Column(String(50), nullable=True)
    pic_position = Column(String(50), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    description_1 = Column(Text, nullable=True)
    description_2 = Column(Text, nullable=True)
    
    # Relationships
    general = relationship("General", back_populates="quotations")
    quotation_resources = relationship("QuotationResources", back_populates="quotation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quotation(id='{self.id}', title='{self.title}')>"