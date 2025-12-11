# app/models/machine.py
from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base

class Machine(Base):
    __tablename__ = "machine"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    creator = Column(String(25), ForeignKey("account.account_id"), nullable=False)  # 추가!
    description = Column(Text, nullable=True)  # 추가!
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    # Relationships
    machine_resources = relationship("MachineResources", back_populates="machine", cascade="all, delete-orphan")
    account = relationship("Account", back_populates="machines")  # 추가!
    
    def __repr__(self):
        return f"<Machine(id='{self.id}', name='{self.name}', creator='{self.creator}')>"