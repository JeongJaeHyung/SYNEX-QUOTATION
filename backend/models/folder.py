# app/models/detailed.py
from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base

class Folder(Base):
    __tablename__ = "folder"
    
    # 1. ID (Primary Key, UUID)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 2. Foreign Keys (SQLite 배치 모드 에러 방지를 위해 name 지정 필수)
    general_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("general.id", ondelete="CASCADE", name="fk_detailed_general_id"), 
        nullable=False
    )
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, 
        server_default=func.current_timestamp(), 
        onupdate=func.current_timestamp()
    )
    
    general = relationship("General", back_populates="folders")
    headers = relationship("Header", back_populates="folder", cascade="all, delete-orphan")
    detaileds = relationship("Detailed", back_populates="folder", cascade="all, delete-orphan")
    price_compares = relationship("PriceCompare", back_populates="folder", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Folder(id='{self.id}', general_id='{self.general_id}')>"