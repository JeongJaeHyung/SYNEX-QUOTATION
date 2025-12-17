#app/models/general.py

from sqlalchemy import Column, String, TIMESTAMP, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base
from db_types import UUID

class General(Base):
    __tablename__ = "general"
    
    # ID (Primary Key, UUID)만 사용, 중복 uuid 컬럼 제거
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    client = Column(String(50), nullable=True)
    creator = Column(String(25), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    description = Column(Text, nullable=True)
    
    # Relationships
    quotations = relationship("Quotation", back_populates="general", cascade="all, delete-orphan")
    detaileds = relationship("Detailed", back_populates="general", cascade="all, delete-orphan")
    price_compares = relationship("PriceCompare", back_populates="general", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<General(id='{self.id}', name='{self.name}')>"