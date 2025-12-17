# app/models/detailed.py

from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base
from db_types import UUID

class Detailed(Base):
    __tablename__ = "detailed"
    
    # ID (Primary Key, UUID)만 사용, 중복 uuid 컬럼 제거
    id = Column(UUID, primary_key=True, default=uuid.uuid4)

    # FK to general
    general_id = Column(UUID, ForeignKey("general.id", ondelete="CASCADE"), nullable=False)
    
    creator = Column(String(25), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    description = Column(Text, nullable=True)
    
    # Relationships
    general = relationship("General", back_populates="detaileds")
    detailed_resources = relationship("DetailedResources", back_populates="detailed", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Detailed(id='{self.id}', general_id='{self.general_id}')>"