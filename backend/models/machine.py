# app/models/machine.py (수정 버전)

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
    manufacturer = Column(String(50), nullable=True)
    client = Column(String(50), nullable=True)
    creator = Column(String(25), nullable=False)
    price = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    machine_resources = relationship("MachineResources", back_populates="machine", cascade="all, delete-orphan")
    
    # 💡 [추가] price_compare_machine과의 관계
    price_compare_machines = relationship("PriceCompareMachine", back_populates="machine", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Machine(id='{self.id}', name='{self.name}')>"