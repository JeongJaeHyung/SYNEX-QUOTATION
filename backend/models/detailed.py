# app/models/detailed.py
from sqlalchemy import Column, String, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base

class Detailed(Base):
    __tablename__ = "detailed"
    
    # 1. ID (Primary Key, UUID)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # 2. Foreign Keys (SQLite 배치 모드 에러 방지를 위해 name 지정 필수)
    general_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("general.id", ondelete="CASCADE", name="fk_detailed_general_id"), 
        nullable=False
    )
    price_compare_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("price_compare.id", ondelete="CASCADE", name="fk_detailed_price_compare_id"), 
        nullable=False
    )
    
    # 3. Data Columns
    creator = Column(String(25), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, 
        server_default=func.current_timestamp(), 
        onupdate=func.current_timestamp()
    )
    description = Column(Text, nullable=True)
    
    # 4. Relationships
    general = relationship("General", back_populates="detaileds")
    # detailed_resources와의 관계 (CASCADE 설정 포함)
    detailed_resources = relationship(
        "DetailedResources", 
        back_populates="detailed", 
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Detailed(id='{self.id}', general_id='{self.general_id}', pc_id='{self.price_compare_id}')>"