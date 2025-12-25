# backend/models/general.py
from sqlalchemy import Column, String, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base

class General(Base):
    __tablename__ = "general"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    client = Column(String(50), nullable=True)
    creator = Column(String(25), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    description = Column(Text, nullable=True)
    
    # 💡 관계 수정: 이제 General은 Folder만 직접 관리합니다.
    # Header, Detailed, PriceCompare는 Folder 모델의 자식으로 이미 설정되어 있습니다.
    folders = relationship("Folder", back_populates="general", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<General(id='{self.id}', name='{self.name}')>"