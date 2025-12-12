# app/models/machine.py
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base

class Machine(Base):
    __tablename__ = "machine"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    manufacturer = Column(String(50), nullable=True)  # 제조사
    client = Column(String(50), nullable=True)         # 고객사
    creator = Column(String(25), nullable=False)       # 작성자
    price = Column(Integer, nullable=True)             # 총 가격
    description = Column(Text, nullable=True)          # 비고
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    machine_resources = relationship("MachineResources", back_populates="machine", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Machine(id='{self.id}', name='{self.name}')>"