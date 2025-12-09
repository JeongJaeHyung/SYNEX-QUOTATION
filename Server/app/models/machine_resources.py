# app/models/machine_resources.py
from sqlalchemy import Column, String, Integer, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class MachineResources(Base):
    __tablename__ = "machine_resources"
    
    # 복합 PK
    machine_id = Column(UUID(as_uuid=True), primary_key=True)
    maker_id = Column(String(4), primary_key=True)
    resources_id = Column(String(6), primary_key=True)
    
    # 데이터 컬럼
    solo_price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Relationships
    machine = relationship("Machine", back_populates="machine_resources")
    resource = relationship(
        "Resources",
        foreign_keys=[maker_id, resources_id],
        primaryjoin="and_(MachineResources.maker_id==Resources.maker_id, MachineResources.resources_id==Resources.id)"
    )
    
    # 복합 FK 제약조건
    __table_args__ = (
        ForeignKeyConstraint(
            ['machine_id'],
            ['machine.id'],
            ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['maker_id', 'resources_id'],
            ['resources.maker_id', 'resources.id']
        ),
    )
    
    def __repr__(self):
        return f"<MachineResources(machine_id='{self.machine_id}', maker_id='{self.maker_id}', resources_id='{self.resources_id}', quantity={self.quantity})>"